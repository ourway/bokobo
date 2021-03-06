"""order added to database

Revision ID: 5430b3b87de2
Revises: cce5582bdca1
Create Date: 2019-07-24 12:01:20.372780

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5430b3b87de2'
down_revision = 'cce5582bdca1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('person_id', postgresql.UUID(), nullable=False))
    op.add_column('orders', sa.Column('total_price', sa.Float(), nullable=True))
    op.alter_column('orders', 'status',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.create_foreign_key(None, 'orders', 'persons', ['person_id'], ['id'])
    op.drop_column('orders', 'items')
    op.drop_column('orders', 'title')
    op.drop_column('orders', 'owner')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('owner', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('items', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.alter_column('orders', 'status',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('orders', 'total_price')
    op.drop_column('orders', 'person_id')
    # ### end Alembic commands ###
