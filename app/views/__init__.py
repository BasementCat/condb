from flask_admin.contrib.sqla import ModelView

from app import admin
from app import models


import arrow

import sqlalchemy_utils as sau

from app import db


class CustomModelView(ModelView):
    @property
    def column_exclude_list(self):
        return ['created_at', 'updated_at']


class ConventionLocationModelView(CustomModelView):
    form_excluded_columns = ['distances']

    def on_model_change(self, form, model, is_created=False):
        with db.session.no_autoflush:
            if not (model.latitude and model.longitude):
                model.get_lat_lon()
            model.get_distances()


admin.add_view(CustomModelView(models.ConventionType, db.session))
admin.add_view(CustomModelView(models.ConventionTheme, db.session))
admin.add_view(ConventionLocationModelView(models.ConventionLocation, db.session))
admin.add_view(CustomModelView(models.Convention, db.session))
admin.add_view(CustomModelView(models.ConventionYear, db.session))
