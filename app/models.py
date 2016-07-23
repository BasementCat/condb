import math

import arrow
import requests

import sqlalchemy_utils as sau

from app import db


class Model(db.Model):
    __abstract__ = True
    created_at = db.Column(sau.ArrowType(), index=True, default=arrow.utcnow)
    updated_at = db.Column(sau.ArrowType(), index=True, default=arrow.utcnow, onupdate=arrow.utcnow)


class NameStrMixin(object):
    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')


class ConventionType(NameStrMixin, Model):
    __tablename__ = 'convention_type'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionTheme(NameStrMixin, Model):
    __tablename__ = 'convention_theme'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionLocation(Model):
    __tablename__ = 'convention_location'

    id = db.Column(db.BigInteger(), primary_key=True)
    country_code = db.Column(db.Unicode(6), index=True, nullable=False)
    state_province = db.Column(db.Unicode(128), index=True)
    city = db.Column(db.Unicode(128), index=True)
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())

    def __unicode__(self):
        return u', '.join(filter(None, [self.country_code, self.state_province, self.city]))

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_lat_lon(self):
        url = 'http://nominatim.openstreetmap.org/search/{}?format=json&limit=1'.format(str(self))
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        self.latitude = data[0]['lat']
        self.longitude = data[0]['lon']

    def straight_line_distance_to(self, other_loc):
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
            if loc is not self and (not self.id or not ConventionLocationDistance.query.filter(ConventionLocationDistance.location_a == self, ConventionLocationDistance.location_b == loc).first()):
                db.session.add(ConventionLocationDistance(
                    location_a=self,
                    location_b=loc,
                    straight_line_distance=self.straight_line_distance_to(loc)
                ))


class ConventionLocationDistance(Model):
    __tablename__ = 'convention_location_distance'

    id = db.Column(db.BigInteger(), primary_key=True)
    location_a_id = db.Column(db.BigInteger(), db.ForeignKey('convention_location.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    location_a = db.relationship('ConventionLocation', foreign_keys=[location_a_id], backref='distances')
    location_b_id = db.Column(db.BigInteger(), db.ForeignKey('convention_location.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    location_b = db.relationship('ConventionLocation', foreign_keys=[location_b_id])
    straight_line_distance = db.Column(db.Float())
    driving_distance = db.Column(db.Float())

    def __unicode__(self):
        return u'{} -> {} ({} mi)'.format(str(self.location_a), str(self.location_b), self.straight_line_distance)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Convention(NameStrMixin, Model):
    __tablename__ = 'convention'

    id = db.Column(db.BigInteger(), primary_key=True)
    was_previously_id = db.Column(db.BigInteger(), db.ForeignKey('convention.id', onupdate='CASCADE', ondelete='CASCADE'))
    was_previously = db.relationship('Convention', remote_side=[id], backref='is_now')
    contype_id = db.Column(db.BigInteger(), db.ForeignKey('convention_type.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    contype = db.relationship('ConventionType', backref='conventions')
    name = db.Column(db.Unicode(256), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionYear(Model):
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
