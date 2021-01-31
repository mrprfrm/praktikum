from flask import Blueprint
from flask_restful import Api

from .resources import Movies, Movie

blueprint = Blueprint('movies', __name__)
api = Api(blueprint)
api.add_resource(Movies, '/movies/')
api.add_resource(Movie, '/movies/<string:pk>/')
