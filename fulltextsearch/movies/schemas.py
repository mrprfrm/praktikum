from marshmallow import Schema
from marshmallow.fields import Str, Nested, Pluck, List


class ShortSchema(Schema):
    id = Str()
    name = Str()

    class Meta:
        ordered = True


class MovieSchema(Schema):
    id = Str()
    title = Str()
    description = Str()
    imdb_rating = Str()
    writers = Nested(ShortSchema, many=True)
    actors = Nested(ShortSchema, many=True)
    genre = List(Str())
    director = List(Str())

    class Meta:
        ordered = True
