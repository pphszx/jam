from flask import Blueprint
from flask_cors import CORS

api_blueprint = Blueprint("api", __name__)

CORS(api_blueprint)

from .resources import auth, user  # noqa
