"""
Tests for plugin.py.

Tests are written using the pytest library (https://docs.pytest.org), and you
should read the testing guidelines in the CKAN docs:
https://docs.ckan.org/en/2.9/contributing/testing.html

To write tests for your extension you should install the pytest-ckan package:

    pip install pytest-ckan

This will allow you to use CKAN specific fixtures on your tests.

For instance, if your test involves database access you can use `clean_db` to
reset the database:

    import pytest

    from ckan.tests import factories

    @pytest.mark.usefixtures("clean_db")
    def test_some_action():

        dataset = factories.Dataset()

        # ...

For functional tests that involve requests to the application, you can use the
`app` fixture:

    from ckan.plugins import toolkit

    def test_some_endpoint(app):

        url = toolkit.url_for('myblueprint.some_endpoint')

        response = app.get(url)

        assert response.status_code == 200


To temporary patch the CKAN configuration for the duration of a test you can use:

    import pytest

    @pytest.mark.ckan_config("ckanext.myext.some_key", "some_value")
    def test_some_action():
        pass
"""
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch

from ckan.plugins import toolkit as tk


def test_plugin_imports_on_current_ckan(monkeypatch):
    keycloak_lib = types.ModuleType("keycloak")
    keycloak_lib.KeycloakOpenID = type("KeycloakOpenID", (), {})
    keycloak_lib.KeycloakAdmin = type("KeycloakAdmin", (), {})
    monkeypatch.setitem(sys.modules, "keycloak", keycloak_lib)

    from ckanext.keycloak import views
    import ckanext.keycloak.plugin as plugin

    assert plugin.KeycloakPlugin
    assert views.get_blueprint()
    assert not hasattr(views, "set_repoze_user")


def test_ckan_210_and_newer_login_does_not_import_repoze_helper(monkeypatch):
    try:
        from ckanext.keycloak import views
    except ModuleNotFoundError as exc:
        if exc.name != "keycloak":
            raise
        keycloak_lib = types.ModuleType("keycloak")
        keycloak_lib.KeycloakOpenID = type("KeycloakOpenID", (), {})
        keycloak_lib.KeycloakAdmin = type("KeycloakAdmin", (), {})
        monkeypatch.setitem(sys.modules, "keycloak", keycloak_lib)
        from ckanext.keycloak import views

    user = object()
    with patch.object(tk, "check_ckan_version", return_value=True), \
            patch.object(views, "g", SimpleNamespace(user_obj=user)), \
            patch("ckan.common.login_user", create=True) as login_user:
        views._log_user_into_ckan(object())

    login_user.assert_called_once_with(user)
