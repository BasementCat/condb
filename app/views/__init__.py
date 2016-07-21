from flask_admin.contrib.sqla import ModelView

from app import admin
from app import models


import arrow

import sqlalchemy_utils as sau

from app import db


class CustomModelView(ModelView):
    @property
    def column_exclude_list(self):
        return ('created_at', 'updated_at')
    


admin.add_view(CustomModelView(models.ConventionType, db.session))
admin.add_view(CustomModelView(models.ConventionThemeType, db.session))
admin.add_view(CustomModelView(models.ConventionTheme, db.session))
admin.add_view(CustomModelView(models.ConventionLocation, db.session))
admin.add_view(CustomModelView(models.Convention, db.session))
admin.add_view(CustomModelView(models.ConventionYear, db.session))
