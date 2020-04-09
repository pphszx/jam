from flask.views import MethodView
from flask_jwt_extended import jwt_required

from jam.api import api_blueprint
from jam.models import UserModel


class UserAPI(MethodView):
    """
    User Registration Resource
    """

    @jwt_required
    def get(self):
        return UserModel.return_all()

    @jwt_required
    def delete(self):
        return UserModel.delete_all()


api_blueprint.add_url_rule(
    "/users",
    view_func=UserAPI.as_view("uset_get_api"),
    methods=["GET", "DELETE"],
)
