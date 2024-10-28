"""empty message

Revision ID: 19708a672da1
Revises: ebb84b9e2f6e
Create Date: 2018-05-19 08:01:02.181730

"""

# revision identifiers, used by Alembic.
revision = '19708a672da1'
down_revision = 'ebb84b9e2f6e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pre_pedido', sa.Column('pedido_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'pre_pedido', 'pedido', ['pedido_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'pre_pedido', type_='foreignkey')
    op.drop_column('pre_pedido', 'pedido_id')
    # ### end Alembic commands ###