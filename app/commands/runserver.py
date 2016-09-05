from smtpd import DebuggingServer
import asyncore

from . import manager
from app import get_app


@manager.command
def runserver(host='0.0.0.0', port=8000, debug=True, reloader=True):
    get_app().run(host=host, port=port, debug=debug, use_debugger=debug, use_reloader=reloader)


@manager.command
def smtpd(host='127.0.0.1', port=2525):
    s = DebuggingServer((host, port), None)
    asyncore.loop()
