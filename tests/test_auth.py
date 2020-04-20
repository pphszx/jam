from flask import url_for
from flask_jwt_extended import decode_token

from jam.models import UserModel, TokenModel

from .base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def test_auth_register(self):
        """
        Register first, then find that user
        """

        self.client.post(
            url_for("api.auth_register_api"),
            json=dict(username="xyz", password=self.password),
            headers=self._set_auth_headers(self.token_access),
        )
        target_user = UserModel.find_by_username("xyz")
        self.assertIsNotNone(target_user)

    def test_auth_token(self):
        """
        Create auth token first, then find that token
        """

        json_post = self.client.post(
            url_for("api.auth_token_api"),
            json=dict(username=self.username, password=self.password),
            headers=self._set_auth_headers(),
        ).get_json()
        access_token_jti = decode_token(json_post["access_token"])["jti"]
        refresh_token_jti = decode_token(json_post["refresh_token"])["jti"]

        target_tokens = TokenModel.get_user_tokens(self.username)
        self.assertIn(access_token_jti, [x.jti for x in target_tokens])
        self.assertIn(refresh_token_jti, [x.jti for x in target_tokens])

    def test_auth_token_refresh(self):
        """
        Refresh auth token first, then find that token
        """

        json_post = self.client.post(
            url_for("api.auth_token_refresh_api"),
            headers=self._set_auth_headers(self.token_refresh),
        ).get_json()
        access_token_jti = decode_token(json_post["access_token"])["jti"]

        target_tokens = TokenModel.get_user_tokens(self.username)
        self.assertIn(access_token_jti, [x.jti for x in target_tokens])

    def test_auth_token_revoke(self):
        """
        Revoke auth token first, then check all tokens
        """

        self.client.put(
            url_for("api.auth_token_revoke_api", token_id=2),
            json=dict(revoke=True),
            headers=self._set_auth_headers(self.token_access),
        )

        target_tokens = TokenModel.get_user_tokens(self.username)

        self.assertTrue(target_tokens[1].revoked)

    def test_auth_logout_access(self):
        """
        Revoke access token first, then check accessibility
        """

        self.client.post(
            url_for("api.auth_logout_access_api"),
            headers=self._set_auth_headers(self.token_access),
        )

        target_tokens = TokenModel.get_user_tokens(self.username)
        self.assertTrue(target_tokens[0].revoked)

    def test_auth_logout_refresh(self):
        """
        Revoke refresh token first, then check accessibility
        """

        self.client.post(
            url_for("api.auth_logout_refresh_api"),
            headers=self._set_auth_headers(self.token_refresh),
        )

        target_tokens = TokenModel.get_user_tokens(self.username)
        self.assertTrue(target_tokens[1].revoked)
