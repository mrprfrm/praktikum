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
    DIRECTOR = 'DIRECTOR'
    WRITER = 'WRITER'
    ACTOR = 'ACTOR'


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


@ipipeline(source='movies')
def upload_movie(data, insert):
    movie = Movie(
        title=data['title'],
        plot=data['plot'] if data['plot'] not in ['N/A', None] else None,
        imdb_rating=data['imdb_rating'] if data['imdb_rating'] not in ['N/A', None] else None
    )
    insert('movies', movie)
    logger.info('Movie created')
    return data, movie


@pipeline(prev='upload_movie')
def upload_genres(data, insert):
    row, movie = data
    for genre in row['genre'].replace(' ', '').split(','):
        genre = Genre(name=genre)
        through = MovieGenre(
            movie_id=movie.id,
            genre_id=genre.id
        )
        insert('genres', genre)
        logger.info('MovieGenre created')
        logger.info('MovieGenre created')
        insert('movies_genres', through)


@pipeline(prev='upload_movie')
def upload_writers(data, writers, insert):
    row, movie = data
    writers_ids = [itm['id'] for itm in json.loads(row['writers'])]
    for writer in filter(lambda itm: itm['id'] in writers_ids, writers):
        person = Person(name=writer['name'])
        through = MoviePerson(
            movie_id=movie.id,
            person_id=person.id,
            position=Position.WRITER
        )
        insert('persons', person)
        logger.info('Person created')
        logger.info('MoviePerson created')
        insert('movies_person', through)


@pipeline(prev='upload_movie')
def upload_directors(data, insert):
    row, movie = data
    for director in row['director'].split(','):
        person = Person(name=director)
        through = MoviePerson(
            movie_id=movie.id,
            person_id=person.id,
            position=Position.DIRECTOR
        )
        insert('persons', person)
        logger.info('Person created')
        logger.info('MoviePerson created')
        insert('movies_person', through)


@pipeline(prev='upload_movie')
def upload_actors(data, insert):
    row, movie = data
    for actor_name in row['actors_names'].split(',') if row['actors_names'] else []:
        person = Person(name=actor_name)
        through = MoviePerson(
            movie_id=movie.id,
            person_id=person.id,
            position=Position.ACTOR
        )
        insert('persons', person)
        logger.info('Person created')
        logger.info('MoviePerson created')
        insert('movies_person', through)
