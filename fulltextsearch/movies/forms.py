from enum import Enum, EnumMeta

from wtforms import Form, IntegerField, StringField, SelectField

from wtforms.validators import NumberRange


class ChoiceMeta(EnumMeta):
    def __iter__(cls):
        for name in cls._member_names_:
            yield cls._member_map_[name], cls._member_map_[name]


class SortType(Enum, metaclass=ChoiceMeta):
    ID = 'id'
    TITLE = 'title'
    IMDB_RATING = 'imdb_rating'

    def __str__(self):
        return self.value


class SortOrder(Enum, metaclass=ChoiceMeta):
    ASCENDING = 'asc'
    DECENDING = 'desc'

    def __str__(self):
        return self.value


class MoviesParametersFilter(Form):
    limit = IntegerField(validators=[NumberRange(min=0)])
    page = IntegerField(validators=[NumberRange(min=1)], default=1)
    search = StringField(default='')
    sort = SelectField(choices=SortType, default=SortType.ID)
    sort_order = SelectField(choices=SortOrder, default=SortOrder.ASCENDING)

    @property
    def filter_query(self):
        query = {
            'size': self.limit.data,
            'from': (self.page.data - 1) * self.limit.data,
            'sort': [{self.sort.data: self.sort_order.data}],
            '_source': ['id', 'title', 'imdb_rating']
        }

        if self.search.data:
            query = {
                **query,
                'query': {
                    'multi_match': {
                        'query': self.search,
                        'fuzziness': 'auto',
                        'fields': [
                            'title^5',
                            'description^4',
                            'genre^3',
                            'actors_names^3',
                            'wirters_names^2',
                            'director'
                        ]
                    }
                }
            }

        return query