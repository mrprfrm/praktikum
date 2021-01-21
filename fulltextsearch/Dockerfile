FROM python:3.7.2-alpine

USER root

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    openssl-dev make
RUN apk add bash postgresql-dev

RUN pip install --upgrade pip
RUN pip install poetry

RUN addgroup -g 1000 -S python && adduser -u 1000 -S python -G python
USER python

RUN mkdir home/python/fulltextsearch
WORKDIR home/python/fulltextsearch

ADD pyproject.toml .
RUN poetry install

USER root
RUN apk del --no-cache .build-deps

USER python
COPY --chown=python:python . /home/python/fulltextsearch

EXPOSE 8000
