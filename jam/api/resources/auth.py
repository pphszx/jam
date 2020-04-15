from flask import request, current_app, jsonify
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
)

from jam.api import api_blueprint
from jam.exceptions import TokenNotFound
from jam.models import UserModel, TokenModel


class AuthRegisterAPI(MethodView):
    """
    User Registration Resource
    """

    def post(self):
        if not request.is_json:
            return {"msg": "Missing JSON in request"}, 400

        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username:
            return {"msg": "Missing username parameter"}, 400
        if not password:
            return {"msg": "Missing password parameter"}, 400

        user = UserModel.find_by_username(username)
        if not user:
            try:
                user = UserModel(username=username)
                user.set_password(password)
                user.save_to_db()

                responseObject = {
                    "status": "success",
                    "message": "Successfully registered.",
                }
                return responseObject, 201
            except Exception as e:
                raise
                responseObject = {
                    "status": "fail",
                    "message": str(e),
                }
                return responseObject, 401
        else:
            responseObject = {
                "status": "fail",
                "message": "User already exists. Please Log in.",
            }
            return responseObject, 202


api_blueprint.add_url_rule(
    "/auth/register",
    view_func=AuthRegisterAPI.as_view("auth_register_api"),
    methods=["POST"],
)


class AuthTokenAPI(MethodView):
    """
    User Token Resource
    """

    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        all_tokens = TokenModel.get_user_tokens(current_user)
        ret = [token.to_dict() for token in all_tokens]
        return jsonify(ret), 200

    def post(self):
        if not request.is_json:
            return {"msg": "Missing JSON in request"}, 400

        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username:
            return {"msg": "Missing username parameter"}, 400
        if not password:
            return {"msg": "Missing password parameter"}, 400

        user = UserModel.find_by_username(username)

        if user and user.validate_password(password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)

            TokenModel.save_encoded_token_to_db(
                access_token, current_app.config["JWT_IDENTITY_CLAIM"]
            )
            TokenModel.save_encoded_token_to_db(
                refresh_token, current_app.config["JWT_IDENTITY_CLAIM"]
            )

            return (
                {"access_token": access_token, "refresh_token": refresh_token},
                200,
            )
        return "Invalid username or password.", 400


api_blueprint.add_url_rule(
    "/auth/token",
    view_func=AuthTokenAPI.as_view("auth_token_api"),
    methods=["GET", "POST"],
)


class AuthTokenRefreshAPI(MethodView):
    """
    User Token Refresh Resource
    """

    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        TokenModel.save_encoded_token_to_db(
            access_token, current_app.config["JWT_IDENTITY_CLAIM"]
        )
        return {"access_token": access_token}


api_blueprint.add_url_rule(
    "/auth/refresh",
    view_func=AuthTokenRefreshAPI.as_view("auth_token_refresh_api"),
    methods=["POST"],
)


class AuthTokenRevokeAPI(MethodView):
    """
    Provide a way for a user to revoke/unrevoke their tokens
    """

    @jwt_required
    def put(self, token_id):
        json_data = request.get_json(silent=True)
        if not json_data:
            return jsonify({"msg": "Missing 'revoke' in body"}), 400
        revoke = json_data.get("revoke", None)
        if revoke is None:
            return jsonify({"msg": "Missing 'revoke' in body"}), 400
        if not isinstance(revoke, bool):
            return jsonify({"msg": "'revoke' must be a boolean"}), 400

        current_user = get_jwt_identity()
        try:
            if revoke:
                TokenModel.revoke_token(token_id, current_user)
                return jsonify({"msg": "Token revoked"}), 200
            else:
                TokenModel.unrevoke_token(token_id, current_user)
                return jsonify({"msg": "Token unrevoked"}), 200
        except TokenNotFound:
            return jsonify({"msg": "The specified token was not found"}), 404


api_blueprint.add_url_rule(
    "/auth/token/<token_id>",
    view_func=AuthTokenRevokeAPI.as_view("auth_token_revoke_api"),
    methods=["PUT"],
)


class AuthLogoutAccessAPI(MethodView):
    """
    User Logout Access Resource
    """

    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        try:
            TokenModel.revoke_token(jti=jti)
            return jsonify({"msg": "Access token revoked."}), 200
        except TokenNotFound:
            return jsonify({"msg": "The specified token was not found"}), 404


api_blueprint.add_url_rule(
    "/auth/logout/access",
    view_func=AuthLogoutAccessAPI.as_view("auth_logout_access_api"),
    methods=["POST"],
)


class AuthLogoutRefreshAPI(MethodView):
    """
    User Logout Refresh Resource
    """

    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        try:
            TokenModel.revoke_token(jti=jti)
            return jsonify({"msg": "Refresh token revoked."}), 200
        except TokenNotFound:
            return jsonify({"msg": "The specified token was not found"}), 404


api_blueprint.add_url_rule(
    "/auth/logout/refresh",
    view_func=AuthLogoutRefreshAPI.as_view("auth_logout_refresh_api"),
    methods=["POST"],
)
