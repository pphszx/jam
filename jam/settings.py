import os
import sys


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"


class BaseConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "$secret+string#")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ON = True
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, "data-dev.db")


class TestingConfig(BaseConfig):
    TESTING = True
    JWT_ON = False
    JWT_BLACKLIST_ENABLED = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", prefix + os.path.join(basedir, "data.db"),
    )


conf = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
