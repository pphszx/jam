import os
from datetime import datetime
from functools import wraps

from flask_jwt_extended import (
    verify_jwt_in_request,
    verify_jwt_refresh_token_in_request,
)

from jam.settings import conf


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def is_jwt_on():
    config_name = os.getenv("FLASK_CONFIG", "development")
    return conf[config_name].JWT_ON


def jwt_required(fn):
    """
    A custom decorator from flask_jwt_extend to protect a Flask endpoint.
    Can be used to disable flask_jwt_extend if JWT_ON config is set to Flase.

    If you decorate an endpoint with this, it will ensure that the requester
    has a valid access token before allowing the endpoint to be called. This
    does not check the freshness of the access token.

    See also: :func:`~flask_jwt_extended.fresh_jwt_required`
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if is_jwt_on():
            verify_jwt_in_request()
        return fn(*args, **kwargs)

    return wrapper


def jwt_refresh_token_required(fn):
    """
    A custom decorator from flask_jwt_extend to protect a Flask endpoint.
    Can be used to disable flask_jwt_extend if JWT_ON config is set to Flase.

    If you decorate an endpoint with this, it will ensure that the requester
    has a valid refresh token before allowing the endpoint to be called.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if is_jwt_on():
            verify_jwt_refresh_token_in_request()
        return fn(*args, **kwargs)

    return wrapper
