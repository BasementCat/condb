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

    @property
    def column_filters(self):
        return []

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('user.login', next=request.url))


class HiddenModelViewMixin(object):
    @property
    def column_filters(self):
        return super(HiddenModelViewMixin, self).column_filters + ['is_hidden']


class EditorModelView(CustomModelView):
    def is_accessible(self):
        return super(EditorModelView, self).is_accessible() and current_user.has_roles(['editor', 'admin'])


class AdminModelView(CustomModelView):
    def is_accessible(self):
        return super(AdminModelView, self).is_accessible() and current_user.has_roles('admin')


class ConventionLocationModelView(HiddenModelViewMixin, EditorModelView):
    form_excluded_columns = ['distances', 'convention_years']

    @property
    def column_filters(self):
        return super(HiddenModelViewMixin, self).column_filters + [
            'country_code',
            'state_province',
            'city',
        ]

    def on_model_change(self, form, model, is_created=False):
        with db.session.no_autoflush:
            if not (model.latitude and model.longitude):
                model.get_lat_lon()
            model.get_distances()


class UserModelView(AdminModelView):
    @property
    def column_exclude_list(self):
        return super(UserModelView, self).column_exclude_list + ['password']


class RoleModelView(AdminModelView):
    form_excluded_columns = ['users']


class ConventionTypeModelView(HiddenModelViewMixin, EditorModelView):
    form_excluded_columns = ['conventions']


class ConventionThemeModelView(HiddenModelViewMixin, EditorModelView):
    form_excluded_columns = ['convention_years']


class ConventionModelView(HiddenModelViewMixin, EditorModelView):
    form_excluded_columns = ['years']


class ConventionYearModelView(HiddenModelViewMixin, EditorModelView):
    @property
    def column_filters(self):
        return super(HiddenModelViewMixin, self).column_filters + [
            'convention',
            'theme',
            'location',
            'is_hidden',
            'starts',
            'ends',
            'attendance',
        ]


admin.add_view(UserModelView(models.User, db.session))
admin.add_view(RoleModelView(models.Role, db.session))
admin.add_view(ConventionTypeModelView(models.ConventionType, db.session))
admin.add_view(ConventionThemeModelView(models.ConventionTheme, db.session))
admin.add_view(ConventionLocationModelView(models.ConventionLocation, db.session))
admin.add_view(ConventionModelView(models.Convention, db.session))
admin.add_view(ConventionYearModelView(models.ConventionYear, db.session))
