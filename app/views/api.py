from flask import (
    Blueprint,
    jsonify,
    )

from flask_user import current_user

from app.models import (
    # Used for filtering
    Model,
    HideableMixin,

    # Actual models
    ConventionLocation,
    ConventionLocationDistance,
    Convention,
    ConventionYear,
    )


app = Blueprint('api', __name__)


@app.route('/conventions', methods=['GET'])
def conventions():
    query = ConventionYear.query

    # TODO: filter the query
    # Restrict viewing hidden objects to editors
    if not current_user.is_authenticated or not current_user.has_roles(['editor', 'admin']):
        for model in Model.models_having_mixin(HideableMixin):
            if model is ConventionYear:
                continue
            query = query \
                .join(model) \
                .filter(model.is_hidden == 0)

    conventions = [
        {
            'convention': {
                'contype': {
                    'name': convention_location.convention.contype.name,
                    'description': convention_location.convention.contype.description,
                },
                'name': convention_location.convention.name,
                'description': convention_location.convention.description,
            },
            'theme': {
                'name': convention_location.theme.name,
                'description': convention_location.theme.description,
            },
            'location': {
                'country_code': convention_location.location.country_code,
                'state_province': convention_location.location.state_province,
                'city': convention_location.location.city,
                'address': convention_location.location.address,
                'latitude': convention_location.location.latitude,
                'longitude': convention_location.location.longitude,
            },
            'starts': str(convention_location.starts),
            'ends': str(convention_location.ends),
            'attendance': convention_location.attendance,
        }
        for convention_location in query
    ]

    return jsonify({'conventions': conventions})
