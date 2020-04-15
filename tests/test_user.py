from flask import url_for

from .base import BaseTestCase


class UserTestCase(BaseTestCase):
    def test_user_get(self):
        response = self.client.get(
            url_for("api.user_api"),
            headers=self._set_auth_headers(self.token_access),
        )
        self.assertIn({"username": "abc"}, response.get_json()["users"])

    def test_user_delete(self):
        self.client.delete(
            url_for("api.user_api"),
            headers=self._set_auth_headers(self.token_access),
        )
        response = self.client.get(
            url_for("api.user_api"),
            headers=self._set_auth_headers(self.token_access),
        )
        self.assertListEqual([], response.get_json()["users"])
