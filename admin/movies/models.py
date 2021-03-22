import uuid
from enum import Enum

from sqlalchemy.dialects.postgresql import UUID

from admin.database import db


class PersonPosition(Enum):
    DIRECTOR = 'director'
    WRITER = 'writer'
    ACTOR = 'actor'


class MoviePerson(db.Model):
    __tablename__ = 'content.movies_person'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.movies.id'))
    genre_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.persons.id'))

    position = db.Column(db.Enum(PersonPosition), default=PersonPosition.DIRECTOR)

    movie = db.relationship('Movie', back_populates='persons')
    persons = db.relationship('Movie', back_populates='movies')


class MovieGenre(db.Model):
    __tablename__ = 'content.movies_genres'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movie_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.movies.id'))
    genre_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.genres.id'))

    movie = db.relationship('Movie', back_populates='genres')
    genre = db.relationship('Genre', back_populates='movies')


class Person(db.Model):
    __tablename__ = 'content.persons'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.VARCHAR(255), nullable=False)

    movies = db.relationship('MoviePerson', back_populates='person')


class Genre(db.Model):
    __tablename__ = 'content.genres'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.VARCHAR(255), nullable=False)

    movies = db.relationship('MovieGenre', back_populates='genre')


class Movie(db.Model):
    __tablename__ = 'content.movies'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.VARCHAR(255), nullable=False)
    plot = db.Column(db.TEXT())
    imdb_rating = db.Column(db.DECIMAL(), default=0)

    genres = db.relationship('MovieGenre', back_populates='movie')
    persons = db.relationship('MoviePerson', back_populates='movie')
