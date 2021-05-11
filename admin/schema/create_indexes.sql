ALTER TABLE content.persons ADD PRIMARY KEY (id);

ALTER TABLE content.genres ADD PRIMARY KEY (id);

ALTER TABLE content.movies ADD PRIMARY KEY (id);

ALTER TABLE content.movies_person ADD PRIMARY KEY (id);
ALTER TABLE content.movies_person ADD CONSTRAINT movies_person_movie FOREIGN KEY (movie_id) REFERENCES content.movies;
ALTER TABLE content.movies_person ADD CONSTRAINT movies_person_person FOREIGN KEY (person_id) REFERENCES content.persons;

ALTER TABLE content.movies_genres ADD PRIMARY KEY (id);
ALTER TABLE content.movies_genres ADD CONSTRAINT movies_genres_movie FOREIGN KEY (movie_id) REFERENCES content.movies;
ALTER TABLE content.movies_genres ADD CONSTRAINT movies_genres_genre FOREIGN KEY (genre_id) REFERENCES content.genres;
