import os

from flask import Flask
from .database import init_app as init_db


def create_app():
    app = Flask(__name__)

    username = os.getenv('DBUSER', 'content')
    password = os.getenv('DBPASSWORD', 'content')
    host = os.getenv('DBHOST', 'database')
    port = os.getenv('DBPORT', 5432)
    name = os.getenv('DBNAME', 'postgres')

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET', 'secret'),
        SQLALCHEMY_DATABASE_URI=f'postgres://{username}:{password}@{host}:{port}/{name}'
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_db(app)

    return app
