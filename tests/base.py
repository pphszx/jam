import unittest

from flask import url_for

from jam import create_app
from jam.extensions import db
from jam.models import UserModel


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app("testing")
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        self.username = "abc"
        self.password = "123"
        user = UserModel(username=self.username)
        user.set_password(self.password)
        db.session.add(user)
        db.session.commit()

        response = self.login().get_json()
        self.token_access = response["access_token"]
        self.token_refresh = response["refresh_token"]

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def _set_auth_headers(self, token=None):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if token:
            headers.update({"Authorization": "Bearer " + token})
        return headers

    def login(self, username=None, password=None):
        return self.client.post(
            url_for("api.auth_token_api"),
            json=dict(
                username=username or self.username,
                password=password or self.password,
            ),
            headers=self._set_auth_headers(),
        )

    def logout_access(self, token):
        return self.client.post(
            url_for("api.auth_logout_access_api"),
            headers=self._set_auth_headers(token),
        )

    def logout_refresh(self, token):
        return self.client.post(
            url_for("api.auth_logout_refresh_api"),
            headers=self._set_auth_headers(token),
        )
