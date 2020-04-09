import os

import click
from flask import Flask

from jam.api import api_blueprint
from jam.extensions import db, jwt, migrate
from jam.models import TokenModel
from jam.settings import conf


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")

    app = Flask("jam")
    app.config.from_object(conf[config_name])

    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    # register_errors(app)

    return app


def register_blueprints(app) -> None:
    app.register_blueprint(api_blueprint, url_prefix="/api")


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db, os.path.join("jam", "migrations"))
    jwt.init_app(app)

    @jwt.token_in_blacklist_loader
    def check_if_token_revoked(decoded_token):
        return TokenModel.is_token_revoked(decoded_token)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return "errors/400.html", 400

    @app.errorhandler(404)
    def page_not_found(e):
        return "errors/404.html", 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return "errors/405.html", 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return "errors/500.html", 500


def register_commands(app):
    @app.cli.command()
    @click.option("--drop", is_flag=True, help="Create after drop.")
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm(
                "This will delete the database, do you want to continue?",
                abort=True,
            )
            db.drop_all()
            click.echo("Drop tables.")
        db.create_all()
        click.echo("Initialized database.")

    @app.cli.command()
    def prunetoken():
        """Delete all the expired tokens in the db."""
        TokenModel.prune_database_tokens()
        click.echo("Deleted expired tokens.")


#     @app.cli.command()
#     @click.option(
#         "--username", prompt=True, help="The username used to login."
#     )
#     @click.option(
#         "--password",
#         prompt=True,
#         hide_input=True,
#         confirmation_prompt=True,
#         help="The password used to login.",
#     )
#     def init(username, password):
#         """Building Bluelog, just for you."""

#         click.echo("Initializing the database...")
#         db.create_all()

#         admin = Admin.query.first()
#         if admin is not None:
#             click.echo("The administrator already exists, updating...")
#             admin.username = username
#             admin.set_password(password)
#         else:
#             click.echo("Creating the temporary administrator account...")
#             admin = Admin(
#                 username=username,
#                 blog_title="Bluelog",
#                 blog_sub_title="No, I'm the real thing.",
#                 name="Admin",
#                 about="Anything about you.",
#             )
#             admin.set_password(password)
#             db.session.add(admin)

#         category = Category.query.first()
#         if category is None:
#             click.echo("Creating the default category...")
#             category = Category(name="Default")
#             db.session.add(category)

#         db.session.commit()
#         click.echo("Done.")

#     @app.cli.command()
#     @click.option(
#         "--category", default=10, help="Quantity of categories, default 10."
#     )
#     @click.option(
#         "--post", default=50, help="Quantity of posts, default 50."
#     )
#     @click.option(
#         "--comment", default=500, help="Quantity of comments, default 500."
#     )
#     def forge(category, post, comment):
#         """Generate fake data."""
#         from bluelog.fakes import (
#             fake_admin,
#             fake_categories,
#             fake_posts,
#             fake_comments,
#             fake_links,
#         )

#         db.drop_all()
#         db.create_all()

#         click.echo("Generating the administrator...")
#         fake_admin()

#         click.echo("Generating %d categories..." % category)
#         fake_categories(category)

#         click.echo("Generating %d posts..." % post)
#         fake_posts(post)

#         click.echo("Generating %d comments..." % comment)
#         fake_comments(comment)

#         click.echo("Generating links...")
#         fake_links()

#         click.echo("Done.")
