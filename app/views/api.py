from flask import (
    Blueprint,
    jsonify,
    )

from app.models import (
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
