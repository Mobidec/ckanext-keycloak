#!python3
# -*- coding: utf-8 -*-
r"""
Testing Keycloak API calls necessary for this package
"""
from typing import Tuple
import re

# header from ckanext.keycloak.views:
import logging

from flask import Blueprint
from os import environ

server_url = environ.get('CKANEXT__KEYCLOAK__SERVER_URL')
client_id = environ.get('CKANEXT__KEYCLOAK__CLIENT_ID')
realm_name = environ.get('CKANEXT__KEYCLOAK__REALM_NAME')
redirect_uri = environ.get('CKANEXT__KEYCLOAK__REDIRECT_URI')
client_secret_key = environ.get('CKANEXT__KEYCLOAK__CLIENT_SECRET_KEY')

log = logging.getLogger(__name__)

keycloak = Blueprint('keycloak', __name__, url_prefix='/user')

# additional parameter for test:
keycloak_user = environ.get('CKANEXT__KEYCLOAK__TEST_USER_NAME')
keycloak_password = environ.get('CKANEXT__KEYCLOAK__TEST_USER_PASSWORD')
token = environ.get('CKANEXT__KEYCLOAK__TEST_USER_TOKEN')

# from ckanext.keycloak.keycloak:
from keycloak import KeycloakOpenID, KeycloakAdmin

# additional parameter for keycloak group prefix
keycloak_role_ckan_group_prefix = environ.get('CKANEXT__KEYCLOAK__CKAN_GROUP_PREFIX')  # "CKAN_GROUP_"

from jose import JWTError, jwt


def keycloak_role_to_ckan(keycloak_role_name: str, key_cloak_re_match: str) -> Tuple[str, str]:
    """
    Naming rule which converts from a keycloak role name to CKAN (group name, capacity) pair
    """
    ckan_capacities_asc = ["member", "editor", "admin"]
    cleaned_localpart = re.sub(r'[^\w]', '_', key_cloak_re_match).lower()
    ckan_group_name = cleaned_localpart
    required_capacity = ckan_capacities_asc[0]
    for capacity in ckan_capacities_asc:
        if cleaned_localpart.endswith("_" + capacity):
            required_capacity = capacity
            ckan_group_name = cleaned_localpart.rsplit("_" + capacity, 1)[0]
            break
    return ckan_group_name, required_capacity


if __name__ == '__main__':
    ##% List Keycloak roles beginning with CKAN_GROUP_***
    keycloak_group_re = f"^{keycloak_role_ckan_group_prefix}(.+)$"
    if keycloak_role_ckan_group_prefix:
        keycloak_admin = KeycloakAdmin(server_url=server_url, client_id=client_id, realm_name=realm_name, client_secret_key=client_secret_key)
        keycloak_realm_roles = keycloak_admin.get_realm_roles(brief_representation=True, search_text=keycloak_role_ckan_group_prefix)
        keycloak_realm_roles_ckan_dict = {}
        for keycloak_role_details in keycloak_realm_roles:
            keycloak_role_name = keycloak_role_details['name']
            gre_match = re.match(keycloak_group_re, keycloak_role_name)
            if gre_match is not None:
                keycloak_realm_roles_ckan_dict[keycloak_role_name] = keycloak_role_to_ckan(keycloak_role_name, gre_match[1])
    else:
        keycloak_realm_roles_ckan_dict = {}

    ##% Get user info
    keycloak_client = KeycloakOpenID(
            server_url=server_url, client_id=client_id, realm_name=realm_name, client_secret_key=client_secret_key
        )
    if not token:
        # token is usually provided in the request
        token = keycloak_client.token(username=keycloak_user, password=keycloak_password)
    userinfo_base = keycloak_client.userinfo(token["access_token"])  # previous method: incomplete dict
    if keycloak_role_ckan_group_prefix:
        userinfo = keycloak_client.decode_token(token["access_token"])
        # jwks = keycloak_client.certs()
        # userinfo = jwt.decode(
        #     token["access_token"],
        #     jwks,
        #     algorithms=["RS256"],
        #     options={"verify_aud": False},
        # )
        keycloak_user_roles = userinfo["realm_access"]["roles"]
        keycloak_user_groups = userinfo.get("groups", [])
        role_ckan_group_dict = {}
        for keycloak_role_name in keycloak_user_roles:
            gre_match = re.match(keycloak_group_re, keycloak_role_name)
            if gre_match is not None:
                role_ckan_group_dict[keycloak_role_name] = keycloak_role_to_ckan(keycloak_role_name, gre_match[1])
    else:
        # previous method, does not return groups
        userinfo = userinfo_base
        role_ckan_group_dict = {}

    ##% Operations on CKAN
    # 0. After obtaining CKAN user id
    # 1. Find missing groups
    # 2. List groups to which the user belongs
    # 3. Remove membership from those where the user does not belong, according to CKAN (if member capacity or lower)
    # 4. Add membership to groups where the user is missing

    print("Test")

