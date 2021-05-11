from flask_admin.contrib.sqla import ModelView


class MovieAdmin(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    column_display_all_relations = True
    # form_columns = [ 'computer_id', 'workgroup.name', ]
    # column_list = ('computer.name', 'name', 'workgroup', 'computer.short_description', 'computer.notes',
    #                'computer.station_type.description', 'computer.room.name')