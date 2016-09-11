import logging
import os
import json
import hashlib
import pickle

from flask import (
    Flask,
    render_template,
    flash,
    )
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_user import UserManager, SQLAlchemyAdapter
from flask_mail import Mail
from flask_bootstrap import Bootstrap


apps = {}

db = SQLAlchemy()
admin = Admin(name='condb', template_mode='bootstrap3')
mail = Mail()
bootstrap = Bootstrap()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Config(object):
    CONFIG_DIRS = [
        os.path.join(os.sep, 'etc', 'condb'),
        os.path.expanduser(os.path.join('~', '.config', 'condb')),
        os.path.join(os.path.dirname(__file__), '..', 'config'),
    ]

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_dicts(self, *dicts):
        conf = {}
        for dict_ in dicts:
            conf.update(dict_)
        assert conf, "No configuration to load"
        return self(**conf)

    @classmethod
    def from_files(self, *filenames):
        configs = []
        for filename in filenames:
            with open(filename, 'r') as fp:
                configs.append(json.load(fp))
        assert configs, "No files to load config from"
        return self.from_dicts(*configs)

    @classmethod
    def from_env(self, env=None):
        if env is None:
            env = os.getenv('CONDB_ENV', 'dev')

        files = []
        for dirname in self.CONFIG_DIRS:
            basefile = os.path.join(dirname, 'config-base.json')
            envfile = os.path.join(dirname, 'config-' + env + '.json')
            if os.path.exists(basefile):
                files.append(basefile)
            if os.path.exists(envfile):
                files.append(envfile)
        assert files, "No files to load config from for env: " + env
        return self.from_files(*files)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    admin.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app.models import User
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, app)

    import views
    from views import index as index_app

    app.register_blueprint(index_app.app, url_prefix=None)

    return app


def get_app(config=None, env=None, force_new=False):
    global apps

    if config is None:
        config = Config.from_env(env=env)

    key = hashlib.sha256(pickle.dumps(config)).hexdigest()
    if force_new or key not in apps:
        apps[key] = create_app(config)
    return apps[key]
