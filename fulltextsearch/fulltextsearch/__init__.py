import os

from flask import Flask
from .elastic import init_app
from movies import blueprint as movies_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET', 'secret'),
        ELASTICSEARCH_HOST=os.getenv('ELASTICSEARCH_HOST', 'localhost:9200')
    )
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_app(app)
    app.register_blueprint(movies_blueprint)

    return app
