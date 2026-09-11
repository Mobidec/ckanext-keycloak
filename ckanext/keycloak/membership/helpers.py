#!python3
# -*- coding: utf-8 -*-
r"""
Helper functions used to link the roles from Keycloak to a CKAN
"""
import logging
from typing import List, Dict
from ckanext.keycloak.membership.definitions import CkanCapacityExtended, DatasetCollaborationCleanupMode
from ckanext.keycloak.membership import rules

import ckan.model as model
import ckan.plugins.toolkit as tk

log = logging.getLogger(__name__)


def _api_group_create(group_name: str):
    context = {
        u'ignore_auth': True,
    }
    groupinfo = {"name": group_name, "description": "Created from Keycloak"}
    created_group_dict = tk.get_action(
        u'group_create'
    )(context, groupinfo)
    return created_group_dict

def _api_group_show(group_id: str, include_users: bool = True):
    context = {
        u'ignore_auth': True,
    }
    args = {"id": group_id, "include_users": include_users}
    group_dict = tk.get_action(
        u'group_show'
    )(context, args)
    return group_dict

def _api_group_member_create(group_id: str, username: str, capacity: str):
    context = {
        u'ignore_auth': True,
    }
    args = {"id": group_id, "username": username, "role": capacity}
    group_dict = tk.get_action(
        u'group_member_create'
    )(context, args)
    return group_dict

def _api_group_member_delete(group_id: str, username: str):
    context = {
        u'ignore_auth': True,
    }
    args = {"id": group_id, "username": username}
    group_dict = tk.get_action(
        u'group_member_delete'
    )(context, args)
    return group_dict

def _api_package_collaborator_list_for_user(user_id: str, capacity:str = None) -> List[Dict[str, str]]:
    context = {
        u'ignore_auth': True,
    }
    args = {"id": user_id}
    if capacity is not None:
        args["capacity"] = capacity
    package_collaboration_list = tk.get_action(
        u'package_collaborator_list_for_user'
    )(context, args)
    return package_collaboration_list

def _api_package_collaborator_delete(package_id: str, user_id: str) -> List[dict]:
    context = {
        u'ignore_auth': True,
    }
    args = {"id": package_id, "user_id": user_id}
    _ = tk.get_action(
        u'package_collaborator_delete'
    )(context, args)
    return _


def update_user_from_keycloak(keycloak_userinfo: dict, keycloak_roles: List[str], ckan_user_id: str) -> None:
    # A. Propagate Keycloak roles to CKAN groups
    # 1. extract CKAN groups from userinfo
    keycloak_user_roles = keycloak_userinfo["realm_access"]["roles"]
    # keycloak_user_groups = userinfo.get("groups", [])
    user_ckan_group_capacity_dict = {}
    for keycloak_role_name in keycloak_user_roles:
        ckan_group_name, required_capacity = rules.keycloak_role_to_ckan(keycloak_role_name)
        if ckan_group_name is not None:
            previous_capacity = user_ckan_group_capacity_dict.get(ckan_group_name, CkanCapacityExtended.Member)
            user_ckan_group_capacity_dict[ckan_group_name] = max(required_capacity, previous_capacity)

    # 2. extract all CKAN groups managed from Keycloak from keycloak_roles
    keycloak_ckan_group_capacity_dict = {}
    for keycloak_role_name in keycloak_roles:
        ckan_group_name, required_capacity = rules.keycloak_role_to_ckan(keycloak_role_name)
        if ckan_group_name is not None:
            previous_capacity = keycloak_ckan_group_capacity_dict.get(ckan_group_name, CkanCapacityExtended.Member)
            keycloak_ckan_group_capacity_dict[ckan_group_name] = max(required_capacity, previous_capacity)

    # 3. Detect and apply changes on groups
    for ckan_group_name, max_capacity in keycloak_ckan_group_capacity_dict.items():
        o_ckan_group = model.Group.by_name(ckan_group_name)
        if o_ckan_group is None:
            log.info(f"Creating group '{ckan_group_name}' from Keycloak role")
            d_ckan_group = _api_group_create(ckan_group_name)
            group_id = d_ckan_group["id"]
        else:
            group_id = o_ckan_group.id
        group_dict = _api_group_show(group_id, include_users=True)
        group_users_dict = {user["id"]: user["capacity"] for user in group_dict["users"]}
        current_capacity = group_users_dict.get(ckan_user_id, None)
        required_capacity = user_ckan_group_capacity_dict.get(ckan_group_name, None)
        if required_capacity is None:
            # user should not make part of the group
            if (current_capacity is not None and
                    ((not rules.permissive_mode)
                     or (current_capacity <= max_capacity))):
                # user is member, with minimum capacities: membership is to be removed
                log.info(f"Removing user from group '{ckan_group_name}' according to Keycloak roles")
                _api_group_member_delete(group_id, ckan_user_id)
        elif ((current_capacity is None
               or current_capacity < required_capacity
               or ((not rules.permissive_mode) and current_capacity > required_capacity))
              and not required_capacity == CkanCapacityExtended.Dataset):
            # user is not member or has lower capacities than required
            if current_capacity is None:
                log.info(f"Adding user to group '{ckan_group_name}' as {required_capacity} according to Keycloak roles")
            else:
                log.info(f"Changing user capacity on group '{ckan_group_name}' to {required_capacity} according to Keycloak roles")
            _api_group_member_create(group_id, ckan_user_id, str(required_capacity))

    # B. Apply changes to dataset collaborations:
    # remove users which are collaborators of datasets where at least one group is listed in Keycloak and the user belongs to none
    cleanup_mode = DatasetCollaborationCleanupMode.from_str(rules.dataset_collaborators_cleanup_mode)
    if not cleanup_mode == DatasetCollaborationCleanupMode.Disabled:
        # 1. List datasets on which the user has membership
        package_collaboration_list = _api_package_collaborator_list_for_user(ckan_user_id)

        # 2. Compare the groups of each package to the lists
        keycloak_ckan_groups = set(keycloak_ckan_group_capacity_dict.items())
        user_ckan_groups = set(user_ckan_group_capacity_dict.items())
        for package_collaboration_dict in package_collaboration_list:
            package_id = package_collaboration_dict["package_id"]
            collaboration_capacity = package_collaboration_dict["capacity"]
            o_package = model.Package.get(package_id)
            package_groups = {o_group.name for o_group in o_package.get_groups()}
            is_mandated_package = len(package_groups.intersection(keycloak_ckan_groups)) > 0
            is_authorized_user = len(package_groups.intersection(user_ckan_groups)) > 0
            if ((is_mandated_package or cleanup_mode == DatasetCollaborationCleanupMode.Complete)
                    and not is_authorized_user):
                # remove collaborator if any group is managed by Keycloak roles and user does not belong to any of these
                log.info(f"Removing user from collaborators of dataset '{o_package.name}' according to Keycloak roles")
                _api_package_collaborator_delete(o_package.id, ckan_user_id)



