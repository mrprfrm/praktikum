import json
import uuid
import sqlite3
from enum import Enum
from typing import Optional

import psycopg2
import psycopg2.extras
from pydantic import Field
from pydantic.main import BaseModel
from loguru import logger

from pipelines import pipeline, context, ipipeline


class Movie(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    plot: Optional[str]
    imdb_rating: Optional[float] = Field(default=0)


class Genre(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str


class Person(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str


class MovieGenre(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    movie_id: uuid.UUID
    genre_id: uuid.UUID


class Position(str, Enum):
    DIRECTOR = 'Режисёр'
    WRITER = 'Сценарист'
    ACTOR = 'Актёр'


class MoviePerson(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    movie_id: uuid.UUID
    person_id: uuid.UUID
    position: Position


@context
def postgresconn():
    psycopg2.extras.register_uuid()
    return psycopg2.connect(
        host='localhost', user='content', password='content', dbname='postgres'
    )


@context
def insert(postgresconn):
    cur = postgresconn.cursor()
    def method(table, instance):
        names = ', '.join(instance.dict().keys())
        params = ', '.join('%s' for itm in range(len(instance.dict().values())))
        cur.execute(
            f'INSERT INTO {table} ({names}) VALUES ({params})',
            list(instance.dict().values())
        )
        postgresconn.commit()
    return method


@context
def movies():
    with sqlite3.connect('instance/db.sqlite') as conn:
        conn.row_factory = sqlite3.Row
        return iter(
            conn.execute(
                '''
                WITH acts AS (
                SELECT m.id, GROUP_CONCAT(a.id) actors_ids, GROUP_CONCAT(a.name) actors_names
                    FROM movies m LEFT JOIN movie_actors ma ON m.id = ma.movie_id
                                  LEFT JOIN actors a ON a.id = ma.actor_id
                    WHERE a.name != 'N/A'
                    GROUP BY m.id
                )
    
                SELECT m.id, genre, director, title, plot, imdb_rating, acts.actors_ids, acts.actors_names,
                   CASE WHEN m.writers = '' THEN '[{"id": "' || m.writer || '"}]'
                        ELSE m.writers
                   END AS writers
                FROM movies m LEFT JOIN acts ON m.id = acts.id;
                '''
            )
        )


@context
def writers():
    with sqlite3.connect('instance/db.sqlite') as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            'SELECT DISTINCT id, name FROM writers WHERE name != "N/A";'
        )


@pipeline()
def upload_movie(data, movies, insert):
    for row in movies:
        movie = Movie(
            title=row['title'],
            plot=row['plot'] if row['plot'] not in ['N/A', None] else None,
            imdb_rating=row['imdb_rating'] if row['imdb_rating'] not in ['N/A', None] else None
        )
        insert('movies', movie)
        logger.info('Movie created')
        yield row, movie


@ipipeline(source='upload_movie')
def upload_genres(data, insert):
    row, movie = data
    for genre in row['genre'].replace(' ', '').split(','):
        genre = Genre(name=genre)
        insert('genres', genre)
        yield movie, genre


@ipipeline(source='upload_genres')
def upload_movie_genre(data, insert):
    movie, genre = data
    through = MovieGenre(
        movie_id=movie.id,
        genre_id=genre.id
    )
    insert('movies_genres', through)


@ipipeline(source='upload_movie')
def upload_writers(data, writers, insert):
    row, movie = data
    writers_ids = [itm['id'] for itm in json.loads(row['writers'])]
    for writer in filter(lambda itm: itm['id'] in writers_ids, writers):
        person = Person(name=writer['name'])
        insert('persons', person)
        yield movie, person


@ipipeline(source='upload_writers')
def upload_movie_writer(data, insert):
    movie, person = data
    through = MoviePerson(
        movie_id=movie.id,
        person_id=person.id,
        position=Position.WRITER
    )
    insert('movies_person', through)


@ipipeline(source='upload_movie')
def upload_directors(data, insert):
    row, movie = data
    for director in row['director'].split(','):
        person = Person(name=director['name'])
        insert('persons', person)
        yield movie, person


@ipipeline(source='upload_directors', )
def upload_movie_director(data, insert):
    movie, person = data
    through = MoviePerson(
        movie_id=movie.id,
        person_id=person.id,
        position=Position.DIRECTOR
    )
    insert('movies_person', through)


@ipipeline(source='upload_movie')
def upload_actors(data, insert):
    row, movie = data
    for actor_name in row['actors_names'].split(',') if row['actors_names'] else []:
        person = Person(name=actor_name)
        insert('persons', person)
        yield movie, person


@ipipeline(source='upload_actors')
def upload_movie_actor(data, insert):
    movie, person = data
    through = MoviePerson(
        movie_id=movie.id,
        person_id=person.id,
        position=Position.ACTOR
    )
    insert('movies_person', through)
