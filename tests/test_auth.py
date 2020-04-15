from flask import url_for
from flask_jwt_extended import decode_token

from .base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def test_auth_register(self):
        """
        Register first, then check all users
        """

        self.client.post(
            url_for("api.auth_register_api"),
            json=dict(username="xyz", password=self.password),
            headers=self._set_auth_headers(self.token_access),
        )
        response = self.client.get(
            url_for("api.user_api"),
            headers=self._set_auth_headers(self.token_access),
        )
        self.assertIn({"username": "xyz"}, response.get_json()["users"])

    def test_auth_token(self):
        """
        Get auth token first, then check all tokens
        """

        json_post = self.client.post(
            url_for("api.auth_token_api"),
            json=dict(username=self.username, password=self.password),
            headers=self._set_auth_headers(),
        ).get_json()
        access_token_jti = decode_token(json_post["access_token"])["jti"]
        refresh_token_jti = decode_token(json_post["refresh_token"])["jti"]

        json_get = self.client.get(
            url_for("api.auth_token_api"),
            json=dict(username=self.username, password=self.password),
            headers=self._set_auth_headers(self.token_access),
        ).get_json()

        self.assertIn(
            access_token_jti, [x["jti"] for x in json_get],
        )
        self.assertIn(
            refresh_token_jti, [x["jti"] for x in json_get],
        )

    def test_auth_token_refresh(self):
        """
        Refresh auth token first, then check all tokens
        """

        json_post = self.client.post(
            url_for("api.auth_token_refresh_api"),
            headers=self._set_auth_headers(self.token_refresh),
        ).get_json()
        access_token_jti = decode_token(json_post["access_token"])["jti"]

        json_get = self.client.get(
            url_for("api.auth_token_api"),
            json=dict(username=self.username, password=self.password),
            headers=self._set_auth_headers(self.token_access),
        ).get_json()

        self.assertIn(
            access_token_jti, [x["jti"] for x in json_get],
        )

    def test_auth_token_revoke(self):
        """
        Revoke auth token first, then check all tokens
        """

        self.client.put(
            url_for("api.auth_token_revoke_api", token_id=2),
            json=dict(revoke=True),
            headers=self._set_auth_headers(self.token_access),
        )

        json_get = self.client.get(
            url_for("api.auth_token_api"),
            json=dict(username=self.username, password=self.password),
            headers=self._set_auth_headers(self.token_access),
        ).get_json()

        self.assertTrue(json_get[1]["revoked"])

    def test_auth_logout_access(self):
        """
        Revoke access token first, then check accessibility
        """

        self.client.post(
            url_for("api.auth_logout_access_api"),
            headers=self._set_auth_headers(self.token_access),
        )

        json_get = self.client.post(
            url_for("api.auth_logout_access_api"),
            headers=self._set_auth_headers(self.token_access),
        ).get_json()

        self.assertEqual(json_get["msg"], "Token has been revoked")

    def test_auth_logout_refresh(self):
        """
        Revoke refresh token first, then check accessibility
        """

        self.client.post(
            url_for("api.auth_logout_refresh_api"),
            headers=self._set_auth_headers(self.token_refresh),
        )

        json_get = self.client.post(
            url_for("api.auth_logout_refresh_api"),
            headers=self._set_auth_headers(self.token_refresh),
        ).get_json()

        self.assertEqual(json_get["msg"], "Token has been revoked")
