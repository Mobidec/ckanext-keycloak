#!python3
# -*- coding: utf-8 -*-
r"""
Keycloak role naming rules for CKAN group membership
"""

from typing import Tuple
import re
from os import environ

from ckan.plugins import toolkit as tk

from ckanext.keycloak.membership.model import CkanCapacity

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


def keycloak_role_to_ckan(keycloak_role_name: str) -> Tuple[str, CkanCapacity] | Tuple[None, None]:
    """
    Naming rule which converts from a keycloak role name to CKAN (group name, capacity) pair
    """
    keycloak_group_re = f"^{keycloak_role_ckan_group_prefix}(.+)$"
    key_cloak_re_match = re.match(keycloak_group_re, keycloak_role_name)
    if key_cloak_re_match is None:
        return None, None
    ckan_capacities_desc = ('admin', 'editor', 'member')
    cleaned_localpart = re.sub(r'[^\w]', '_', key_cloak_re_match[1]).lower()
    ckan_group_name = cleaned_localpart
    s_required_capacity = ckan_capacities_desc[-1]
    for capacity in ckan_capacities_desc:
        if cleaned_localpart.endswith("_" + capacity):
            s_required_capacity = capacity
            ckan_group_name = cleaned_localpart.rsplit("_" + capacity, 1)[0]
            break
    required_capacity = CkanCapacity.from_str(s_required_capacity)
    return ckan_group_name, required_capacity
