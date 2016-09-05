from flask import (
    redirect,
    url_for,
    request,
    )

from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

import arrow

import sqlalchemy_utils as sau

from app import (
    admin,
    models,
    db,
    )


class CustomModelView(ModelView):
    @property
    def column_exclude_list(self):
        return ['created_at', 'updated_at']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user.login', next=request.url))


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
