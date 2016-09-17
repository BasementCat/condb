from flask import (
    Blueprint,
    jsonify,
    request,
    render_template,
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

    if 'application/json' in request.headers.get('Accept', ''):
        conventions = [
            {
                'convention': {
                    'contype': {
                        'name': convention_year.convention.contype.name,
                        'description': convention_year.convention.contype.description,
                    },
                    'name': convention_year.convention.name,
                    'description': convention_year.convention.description,
                },
                'theme': {
                    'name': convention_year.theme.name,
                    'description': convention_year.theme.description,
                },
                'location': {
                    'country_code': convention_year.location.country_code,
                    'state_province': convention_year.location.state_province,
                    'city': convention_year.location.city,
                    'address': convention_year.location.address,
                    'latitude': convention_year.location.latitude,
                    'longitude': convention_year.location.longitude,
                },
                'starts': str(convention_year.starts),
                'ends': str(convention_year.ends),
                'attendance': convention_year.attendance,
            }
            for convention_year in query
        ]

        return jsonify({'conventions': conventions})
    elif 'text/html' in request.headers.get('Accept', ''):
        return render_template('api/conventions.jinja.html', conventions=query.all())
    else:
        abort(400, "Don't know how to send you the right content-type")
