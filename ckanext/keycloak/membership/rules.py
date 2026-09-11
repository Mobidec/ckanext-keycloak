#!python3
# -*- coding: utf-8 -*-
r"""
Keycloak role naming rules for CKAN group membership
"""

from typing import Tuple
import re
from os import environ

from ckan.plugins import toolkit as tk

from ckanext.keycloak.membership.definitions import CkanCapacityExtended

"""
Prefix used to define a CKAN group membership role in Keycloak.
Example: CKAN_GROUP_TEST_GROUP[_EDITOR]
The CKAN group name will be "test_group" (lowercase and replacement of special characters with underscores (_). 
The required capacity associated with this role will be editor. By default, the capacity is member.
If a user is mapped to two roles with the same CKAN group, the user will have the maximum required capacity.
The group membership mappings are limited to those listed in the Keycloak roles. 
"""
keycloak_role_ckan_group_prefix = "CKAN_GROUP_"

"""
In permissive mode, a user which was given higher capacities than those listed by Keycloak roles for a given CKAN group, is left unchanged.
Strict mode (default) enforces exactly the same capacities as defined in the Keycloak role.
"""
permissive_mode = tk.config.get('ckanext.keycloak.user_membership_permissive', environ.get('CKANEXT__KEYCLOAK__USER_MEMBERSHIP_PERMISSIVE'))

"""
Default capacity: capacity used if not specified in the role suffix
Accepted: dataset, member, editor, admin
"""
ckan_default_capacity = tk.config.get('ckanext.keycloak.user_membership_capacity_default', environ.get('CKANEXT__KEYCLOAK__USER_MEMBERSHIP_CAPACITY_DEFAULT', "dataset"))


"""
Dataset collaborators cleanup mode
Accepted: 
- complete: remove collaborators of a package when the groups do not intersect with any of their roles, 
- restricted: same rule, but the package must belong to at least one group listed in Keycloak roles, 
- disabled: never remove package collaborators 
"""
dataset_collaborators_cleanup_mode = tk.config.get('ckanext.keycloak.dataset_collaborators_cleanup_mode', environ.get('CKANEXT__KEYCLOAK__DATASET_COLLABORATORS_CLEANUP_MODE', "restricted"))


def keycloak_role_to_ckan(keycloak_role_name: str) -> Tuple[str, CkanCapacityExtended] | Tuple[None, None]:
    """
    Naming rule which converts from a keycloak role name to CKAN (group name, capacity) pair
    """
    keycloak_group_re = f"^{re.escape(keycloak_role_ckan_group_prefix)}(.+)$"
    key_cloak_re_match = re.match(keycloak_group_re, keycloak_role_name)
    if key_cloak_re_match is None:
        return None, None
    ckan_capacities_desc = ('admin', 'editor', 'member', 'dataset')
    cleaned_localpart = re.sub(r'[^\w]', '_', key_cloak_re_match[1]).lower()
    ckan_group_name = cleaned_localpart
    required_capacity = CkanCapacityExtended.from_str(ckan_default_capacity)
    for capacity in ckan_capacities_desc:
        if cleaned_localpart.endswith("_" + capacity):
            required_capacity = CkanCapacityExtended.from_str(capacity)
            ckan_group_name = cleaned_localpart.rsplit("_" + capacity, 1)[0]
            break
    return ckan_group_name, required_capacity
