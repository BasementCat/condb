import os
import glob

from flask.ext.script import (
    Manager,
    Server,
    )
from flask.ext.migrate import Migrate, MigrateCommand

from app import (
    get_app,
    db,
    )

local_py_files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), '*.py'))
local_pyc_files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), '*.pyc'))
local_files = set([os.path.splitext(os.path.basename(f))[0] for f in local_py_files + local_pyc_files])

__all__ = ['manager'] + list(set([
    filename
    for filename
    in local_files
    if not filename.startswith('_')
]))


app = get_app()
manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
