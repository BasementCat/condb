import logging
import getpass

import arrow

from . import manager
from app import db
from app.models import (
    User,
    Role,
    )


logger = logging.getLogger(__name__)


@manager.option('-a', '--add')
@manager.option('-e', '--edit')
@manager.option('-r', '--add-role')
@manager.option('-R', '--remove-role')
@manager.option('-p', '--password')
@manager.option('-P', '--ask-password', action='store_true')
@manager.option('-m', '--email')
def user(add, edit, add_role, remove_role, password, email, ask_password):
    if add:
        user = User(
            username=add,
            confirmed_at=arrow.utcnow().datetime,
            active=True,
        )
        db.session.add(user)
    elif edit:
        user = User.query.filter(User.username == edit).first()
        if not user:
            print "No such user"
            return

    if add or edit:
        if add or ask_password:
            password = getpass.getpass("Password: ")
            pass_b = getpass.getpass("Retype Password: ")
            if password != pass_b:
                print "Passwords don't match"
                return

        if password:
            user.set_password(password)

        if email:
            user.email = email

        db.session.commit()

        if add_role:
            user.roles.append(Role.query.filter(Role.name == add_role).first())
        if remove_role:
            user.roles.remove(Role.query.filter(Role.name == remove_role).first())

        db.session.commit()
    else:
        for u in User.query:
            print '{} <{}> "{} {}" {}'.format(
                u.username,
                u.email,
                u.first_name,
                u.last_name,
                ', '.join([r.name for r in u.roles])
            )


@manager.command
def role(scaffold=False, add=None, remove=None):
    if scaffold:
        role_names = ['admin', 'editor']
        for role_name in role_names:
            role = Role.query.filter(Role.name == role_name).first()
            if not role:
                db.session.add(Role(name=role_name))
                db.session.commit()

    elif add:
        db.session.add(Role(name=add))
        db.session.commit()

    elif remove:
        db.session.delete(Role.query.filter(Role.name == remove).first())

    else:
        for role in Role.query:
            print role.name
