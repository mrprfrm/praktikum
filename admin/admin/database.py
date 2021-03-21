import click
from flask import g
from flask.cli import with_appcontext
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


def get_db(e=None):
    if not 'db' in g:
        g.db = db


def close_db(e=None):
    db.session.remove()
    g.pop('db', None)


@click.command('init-db')
@with_appcontext
def init_db_command():
    # TODO add models import
    db.create_all()
    click.echo('Initialized the database.')


def init_app(app):
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app)
        app.before_request(get_db)
        app.teardown_appcontext(close_db)
        app.cli.add_command(init_db_command)
