from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from admin.database import db
from movies.models import Movie, Person, Genre, MoviePerson

admin = Admin(name='stream service admin', template_mode='bootstrap3')


def init_app(app):
    admin.init_app(app)

    from movies.admin import MovieAdmin

    admin.add_view(MovieAdmin(Movie, db.session))
    admin.add_view(MovieAdmin(MoviePerson, db.session))
    admin.add_view(ModelView(Genre, db.session))
    admin.add_view(ModelView(Person, db.session))
