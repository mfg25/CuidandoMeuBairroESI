"""empty message

Revision ID: cb6d54a6b8cc
Revises: 66a35500024d
Create Date: 2018-05-26 19:39:14.233490

"""

# revision identifiers, used by Alembic.
revision = 'cb6d54a6b8cc'
down_revision = '66a35500024d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('notification_sent', sa.Boolean(), nullable=False,
                                       server_default='true'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'notification_sent')
    # ### end Alembic commands ###