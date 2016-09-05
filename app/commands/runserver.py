from . import manager
from app import get_app


@manager.command
def runserver(host='0.0.0.0', port=8000, debug=True, reloader=True):
    get_app().run(host=host, port=port, debug=debug, use_debugger=debug, use_reloader=reloader)
