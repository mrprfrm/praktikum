DROP SCHEMA IF EXISTS content CASCADE;

DROP ROLE IF EXISTS content;

CREATE ROLE content WITH LOGIN PASSWORD 'content';

CREATE SCHEMA AUTHORIZATION content;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA content to content;

CREATE TABLE content.persons(
    id UUID NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE content.genres(
    id UUID NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE content.movies(
    id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    plot TEXT,
    imdb_rating DECIMAL DEFAULT 0
);

CREATE TYPE personposition AS ENUM ('Режисёр', 'Сценарист', 'Актёр');

CREATE TABLE content.movies_person(
    id UUID NOT NULL,
    movie_id UUID NOT NULL,
    person_id UUID NOT NULL,
    position personposition
);

CREATE TABLE content.movies_genres(
    id UUID NOT NULL,
    movie_id UUID NOT NULL,
    genre_id UUID NOT NULL
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA content to content;
