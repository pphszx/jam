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
    JWT_ON = bool(os.getenv("JWT_ON", True))
    JWT_BLACKLIST_ENABLED = bool(os.getenv("JWT_BLACKLIST_ENABLED", True))
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URL", prefix + os.path.join(basedir, "data-dev.db")
    )


class TestingConfig(BaseConfig):
    TESTING = True
    JWT_ON = False
    JWT_BLACKLIST_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", prefix + os.path.join(basedir, "data.db"),
    )

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

        # load DATABASE_URI from env
        try:
            DATABASE_DIALECT = os.environ["DATABASE_DIALECT"]
            DATABASE_USER = os.environ["DATABASE_USER"]
            DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
            DATABASE_HOST = os.environ["DATABASE_HOST"]
            DATABASE_PORT = os.environ["DATABASE_PORT"]
            DATABASE_DB = os.environ["DATABASE_DB"]
        except KeyError:
            app.logger.warning(
                "No production configuration found,\
                will create sqlite db data.db"
            )
        else:
            SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
                DATABASE_DIALECT,
                DATABASE_USER,
                DATABASE_PASSWORD,
                DATABASE_HOST,
                DATABASE_PORT,
                DATABASE_DB,
            )
            if app.config.from_mapping(
                {"SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI}
            ):
                app.logger.warning(
                    "Loaded your production configuration from env"
                )


conf = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
