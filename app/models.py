import math

import arrow
import requests

from sqlalchemy.orm import backref
import sqlalchemy_utils as sau

from flask_user import UserMixin

from app import db


class Model(db.Model):
    __abstract__ = True
    created_at = db.Column(sau.ArrowType(), index=True, default=arrow.utcnow)
    updated_at = db.Column(sau.ArrowType(), index=True, default=arrow.utcnow, onupdate=arrow.utcnow)

    @classmethod
    def _truncate_table(self):
        db.engine.execute("TRUNCATE TABLE `{}`;".format(self.__table__.name))

    @classmethod
    def iter_all_models(self):
        queue = [self]
        while queue:
            model = queue.pop()
            yield model
            queue += model.__subclasses__()

    @classmethod
    def models_having_mixin(self, mixin):
        return filter(
            lambda model: issubclass(model, mixin),
            self.iter_all_models()
        )


class NameStrMixin(object):
    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')


class HideableMixin(object):
    is_hidden = db.Column(db.Boolean(), nullable=False, default=False, server_default='0')


class User(UserMixin, Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger(), primary_key=True)

    # User authentication information
    username = db.Column(db.Unicode(128), nullable=False, unique=True)
    password = db.Column(db.Unicode(256), nullable=False, server_default=u'')
    reset_password_token = db.Column(db.Unicode(128), nullable=False, server_default=u'')

    # User email information
    email = db.Column(db.Unicode(256), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default=u'0')
    first_name = db.Column(db.Unicode(128), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(128), nullable=False, server_default=u'')

    # Roles
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    def __unicode__(self):
        return self.username

    def __str__(self):
        return unicode(self).encode('utf-8')


class Role(NameStrMixin, Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(128), unique=True)


class UserRoles(Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    user_id = db.Column(db.BigInteger(), db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.BigInteger(), db.ForeignKey('role.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)


class ConventionType(HideableMixin, NameStrMixin, Model):
    __tablename__ = 'convention_type'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionTheme(HideableMixin, NameStrMixin, Model):
    __tablename__ = 'convention_theme'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionLocation(HideableMixin, Model):
    __tablename__ = 'convention_location'

    id = db.Column(db.BigInteger(), primary_key=True)
    country_code = db.Column(db.Unicode(6), index=True, nullable=False)
    state_province = db.Column(db.Unicode(128), index=True)
    city = db.Column(db.Unicode(128), index=True)
    address = db.Column(db.Unicode(256), index=True)
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())

    def __unicode__(self):
        return u', '.join(filter(None, [self.country_code, self.state_province, self.city, self.address]))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_lat_lon(self):
        url = 'http://nominatim.openstreetmap.org/search/{}?format=json&limit=1'.format(str(self))
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        if data:
            self.latitude = data[0]['lat']
            self.longitude = data[0]['lon']

    def straight_line_distance_to(self, other_loc):
        if self.latitude is None or self.longitude is None:
            return

        # https://gist.github.com/rochacbruno/2883505
        lat1 = float(self.latitude)
        lon1 = float(self.longitude)
        lat2 = float(other_loc.latitude)
        lon2 = float(other_loc.longitude)
        # radius = 6371 # km
        radius = 3961 # mi

        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c

        return d

    def get_distances(self):
        for loc in ConventionLocation.query:
            if self.latitude is None or self.longitude is None or loc.latitude is None or loc.longitude is None:
                continue

            existing_dist = ConventionLocationDistance.query.filter(
                ((ConventionLocationDistance.location_a == self) & (ConventionLocationDistance.location_b == loc))
                | ((ConventionLocationDistance.location_a == loc) & (ConventionLocationDistance.location_b == self))
            ).first()
            if loc is not self and (not self.id or not existing_dist):
                db.session.add(ConventionLocationDistance(
                    location_a=self,
                    location_b=loc,
                    straight_line_distance=self.straight_line_distance_to(loc)
                ))


class ConventionLocationDistance(Model):
    __tablename__ = 'convention_location_distance'

    id = db.Column(db.BigInteger(), primary_key=True)
    location_a_id = db.Column(db.BigInteger(), db.ForeignKey('convention_location.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    location_a = db.relationship('ConventionLocation', foreign_keys=[location_a_id], backref=backref('distances', cascade='all, delete-orphan'))
    location_b_id = db.Column(db.BigInteger(), db.ForeignKey('convention_location.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    location_b = db.relationship('ConventionLocation', foreign_keys=[location_b_id], backref=backref('distances_b', cascade='all, delete-orphan'))
    straight_line_distance = db.Column(db.Float())
    driving_distance = db.Column(db.Float())

    def __unicode__(self):
        return u'{} -> {} ({} mi)'.format(str(self.location_a), str(self.location_b), self.straight_line_distance)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Convention(HideableMixin, NameStrMixin, Model):
    __tablename__ = 'convention'

    id = db.Column(db.BigInteger(), primary_key=True)
    was_previously_id = db.Column(db.BigInteger(), db.ForeignKey('convention.id', onupdate='CASCADE', ondelete='CASCADE'))
    was_previously = db.relationship('Convention', remote_side=[id], backref='is_now')
    contype_id = db.Column(db.BigInteger(), db.ForeignKey('convention_type.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    contype = db.relationship('ConventionType', backref='conventions')
    name = db.Column(db.Unicode(256), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionYear(HideableMixin, Model):
    __tablename__ = 'convention_year'

    id = db.Column(db.BigInteger(), primary_key=True)
    convention_id = db.Column(db.BigInteger(), db.ForeignKey('convention.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    convention = db.relationship('Convention', backref='years')
    theme_id = db.Column(db.BigInteger(), db.ForeignKey('convention_theme.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    theme = db.relationship('ConventionTheme', backref='convention_years')
    location_id = db.Column(db.BigInteger(), db.ForeignKey('convention_location.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    location = db.relationship('ConventionLocation', backref='convention_years')
    starts = db.Column(db.Date())
    ends = db.Column(db.Date())
    attendance = db.Column(db.Integer())

    def __unicode__(self):
        return u'[{}] {} {}: {} ({})'.format(
            self.convention.contype.name,
            self.convention.name,
            arrow.get(self.starts).format('YYYY'),
            self.theme.name,
            self.attendance
        )

    def __str__(self):
        return unicode(self).encode('utf-8')
