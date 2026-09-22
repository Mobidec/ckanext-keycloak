import logging
from keycloak import KeycloakOpenID, KeycloakAdmin
log = logging.getLogger(__name__)

class KeycloakClient:
    def __init__(self, server_url, client_id, realm_name, client_secret_key):
        self.server_url = server_url
        self.client_id = client_id
        self.realm_name = realm_name
        self.client_secret_key = client_secret_key
        
    def get_keycloak_client(self):
        return KeycloakOpenID(
            server_url=self.server_url, client_id=self.client_id, realm_name=self.realm_name, client_secret_key=self.client_secret_key
        )

    def get_auth_url(self, redirect_uri):
        return self.get_keycloak_client().auth_url(redirect_uri=redirect_uri, scope="openid profile email")

    def get_token(self, code, redirect_uri):
        token = self.get_keycloak_client().token(grant_type="authorization_code", code=code, redirect_uri=redirect_uri)
        return token

    def get_user_info(self, token):
        # return self.get_keycloak_client().userinfo(token.get('access_token'))
        return self.get_keycloak_client().decode_token(token.get('access_token'))

    def get_user_groups(self, token):
        return self.get_keycloak_client().userinfo(token).get('groups', [])

    def get_keycloak_admin(self):
        return KeycloakAdmin(
            server_url=self.server_url, client_id=self.client_id, realm_name=self.realm_name, client_secret_key=self.client_secret_key
        )

    def get_keycloak_realm_roles(self, search_text:str=None, brief_representation: bool=True):
        return self.get_keycloak_admin().get_realm_roles(brief_representation=brief_representation, search_text=search_text)

    def revoke_user_session(self, refresh_token) -> None:
        if not refresh_token:
            log.debug("No token provided for logout - user might already be logged out")
            return
        try:
            self.get_keycloak_client().logout(refresh_token)
            log.info("Successfully revoked Keycloak session via API.")
        except Exception as e:
            log.error(f"Failed to revoke Keycloak token during logout: {str(e)}")
