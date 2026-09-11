#!python3
# -*- coding: utf-8 -*-
r"""
Calling CKAN API to get an example response
"""
from typing import Tuple
import re

# header from ckanext.keycloak.views:
import logging

from flask import Blueprint
from os import environ

from ckanapi_harvesters import CkanApi

ckan_url = environ.get('CKAN_URL')
ckan_token = environ.get('CKAN_API_KEY')


if __name__ == '__main__':
    ckan = CkanApi(ckan_url, apikey=ckan_token)

    user_info = ckan.query_current_user()
    user_id = user_info.id

    package_collaborations = ckan.package_collaborator_list_for_user(user_id)

    package_list = ckan.package_search_all(limit_per_request=10, search_all=False, include_private=True)
    package_info = package_list[0]
    package_id = package_info.id

    group_info = package_info.groups[0]
    group_id = group_info.id


    print("Test")

