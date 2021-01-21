import os

from flask import Flask, g
from .elastic import init_app

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

    @app.route('/')
    def index():
        return 'Hello praktikum!'

    return app
