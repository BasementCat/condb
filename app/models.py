import arrow

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


class ConventionThemeType(NameStrMixin, Model):
    __tablename__ = 'convention_theme_type'

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionTheme(NameStrMixin, Model):
    __tablename__ = 'convention_theme'

    id = db.Column(db.BigInteger(), primary_key=True)
    themetype_id = db.Column(db.BigInteger(), db.ForeignKey('convention_theme_type.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    themetype = db.relationship('ConventionThemeType', backref='themes')
    name = db.Column(db.Unicode(64), unique=True, nullable=False)
    description = db.Column(db.UnicodeText())


class ConventionLocation(Model):
    __tablename__ = 'convention_location'

    id = db.Column(db.BigInteger(), primary_key=True)
    country_code = db.Column(db.Unicode(6), index=True, nullable=False)
    state_province = db.Column(db.Unicode(128), index=True)
    city = db.Column(db.Unicode(128), index=True)

    def __unicode__(self):
        return u': '.join(filter(None, [self.country_code, self.state_province, self.city]))

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
