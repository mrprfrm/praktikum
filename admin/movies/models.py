import uuid
from enum import Enum

from sqlalchemy.dialects.postgresql import UUID

from admin.database import db


class PersonPosition(str, Enum):
    DIRECTOR = 'Режисёр'
    WRITER = 'Сценарист'
    ACTOR = 'Актёр'


class MoviePerson(db.Model):
    __tablename__ = 'movies_person'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = db.Column(UUID(as_uuid=True), db.ForeignKey('movies.id'))
    person_id = db.Column(UUID(as_uuid=True), db.ForeignKey('persons.id'))

    position = db.Column(db.Enum(PersonPosition), default=PersonPosition.DIRECTOR)

    movie = db.relationship('Movie', back_populates='persons')
    person = db.relationship('Person', back_populates='movies')


class MovieGenre(db.Model):
    __tablename__ = 'movies_genres'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = db.Column(UUID(as_uuid=True), db.ForeignKey('movies.id'))
    genre_id = db.Column(UUID(as_uuid=True), db.ForeignKey('genres.id'))

    movie = db.relationship('Movie', back_populates='genres')
    genre = db.relationship('Genre', back_populates='movies')


class Person(db.Model):
    __tablename__ = 'persons'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.VARCHAR(255), nullable=False)

    movies = db.relationship('MoviePerson', back_populates='person')


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.VARCHAR(255), nullable=False)

    movies = db.relationship('MovieGenre', back_populates='genre')


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.VARCHAR(255), nullable=False)
    plot = db.Column(db.TEXT())
    imdb_rating = db.Column(db.DECIMAL(), default=0)

    genres = db.relationship('MovieGenre', back_populates='movie')
    persons = db.relationship('MoviePerson', back_populates='movie')
