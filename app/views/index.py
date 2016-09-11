from flask import (
    Blueprint,
    render_template,
    )


app = Blueprint('index', __name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.jinja.html')
