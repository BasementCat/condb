"""User table

Revision ID: f3434da19e06
Revises: a0a0e47b8683
Create Date: 2016-09-05 11:51:12.638838

"""

# revision identifiers, used by Alembic.
revision = 'f3434da19e06'
down_revision = 'a0a0e47b8683'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('created_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=True),
    sa.Column('updated_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.Unicode(length=128), nullable=False),
    sa.Column('password', sa.Unicode(length=256), server_default=u'', nullable=False),
    sa.Column('reset_password_token', sa.Unicode(length=128), server_default=u'', nullable=False),
    sa.Column('email', sa.Unicode(length=256), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=u'0', nullable=False),
    sa.Column('first_name', sa.Unicode(length=128), server_default=u'', nullable=False),
    sa.Column('last_name', sa.Unicode(length=128), server_default=u'', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_created_at'), 'user', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_updated_at'), 'user', ['updated_at'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_updated_at'), table_name='user')
    op.drop_index(op.f('ix_user_created_at'), table_name='user')
    op.drop_table('user')
    ### end Alembic commands ###
