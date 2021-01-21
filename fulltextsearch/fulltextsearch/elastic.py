import json
import os
import sqlite3

import click
from flask import g
from flask.cli import with_appcontext
from flask_elasticsearch import FlaskElasticsearch


MOVIES_SQL = '''
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

WRITERS_SQL = '''
SELECT DISTINCT id, name FROM writers WHERE name != 'N/A';
'''


es = FlaskElasticsearch()


def close_elastic(e=None):
    g.pop('es', None)


@click.command('init-index')
@click.option('--c', '-config', 'conf_path', default='server/elastic.json')
@with_appcontext
def init_index_command(conf_path):
    if os.path.exists(conf_path):
        with open(conf_path) as file:
            try:
                for index, config in json.load(file).items():
                    es.indices.create(index=index, body=config)
                    click.echo(f'Index {index} created.')
            except Exception as err:
                click.echo(err, err=True)
    else:
        click.echo(f'File {conf_path} is not exist.', err=True)


@click.command('etl')
@click.argument('db_path')
@with_appcontext
def etl_command(db_path):
    if os.path.exists(db_path):
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                movies = conn.execute(MOVIES_SQL)
                writers = conn.execute(WRITERS_SQL)
                documents = []
                for movie in sorted(movies, key=lambda itm: itm['id']):
                    actors_ids = movie['actors_ids'].split(',') if movie['actors_ids'] else []
                    actors_names = movie['actors_names'].split(',') if movie['actors_names'] else []
                    actors = [{'id': _id, 'name': name} for _id, name in zip(actors_ids, actors_names)]

                    writers_ids = [itm['id'] for itm in json.loads(movie['writers'])]
                    movie_writers = filter(lambda itm: itm['id'] in writers_ids, writers)

                    directors = [itm.strip() for itm in movie['director'].split(',')]

                    document = {
                        'id': movie['id'],
                        'title': movie['title'],
                        'genre': movie['genre'].replace(' ', '').split(','),
                        'description': movie['plot'] if movie['plot'] != 'N/A' else None,
                        'director': directors if movie['director'] != 'N/A' else None,
                        'imdb_rating': float(movie['imdb_rating']) if movie['imdb_rating'] != 'N/A' else None,
                        'actors': actors,
                        'actors_names': [itm['name'] for itm in actors],
                        'writers': [dict(itm) for itm in movie_writers],
                        'writers_names': [itm['name'] for itm in movie_writers]
                    }
                    index = {'index': {'_index': 'movies', '_id': movie['id'],}}
                    documents.append(index)
                    documents.append(document)
                es.bulk(documents)
                count = len(documents)
                click.echo(f'{count} was added to index movies.')
        except Exception as err:
            click.echo(err, err=True)
    else:
        click.echo(f'File {db_path} is not exist.', err=True)


def init_app(app):
    with app.app_context():
        es.init_app(app)
        app.cli.add_command(init_index_command)
        app.cli.add_command(etl_command)
        app.teardown_appcontext(close_elastic)
        g.es = es
