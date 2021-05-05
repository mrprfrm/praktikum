from elasticsearch import NotFoundError
from flask import request
from flask_restful import Resource, abort

from fulltextsearch.elastic import es
from .forms import MoviesParametersFilter
from .schemas import MovieSchema


class Movie(Resource):
    def get(self, pk):
        try:
            data = es.get('movies', pk)
            schema = MovieSchema()
            return schema.dump(data['_source'])
        except NotFoundError:
            abort(404, message='Movie is not found.')


class Movies(Resource):
    def get(self):
        form = MoviesParametersFilter(request.args)
        if form.validate():
            data = es.search(index='movies', body=form.filter_query)
            source = (itm['_source'] for itm in data['hits']['hits'])
            schema = MovieSchema(many=True, only=('id', 'title', 'imdb_rating'))
            return schema.dump(source)
        return form.errors
