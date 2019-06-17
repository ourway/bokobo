"""library added

Revision ID: 4c15073a6a9a
Revises: 4473e6dd7e1d
Create Date: 2019-06-16 10:45:29.294669

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4c15073a6a9a'
down_revision = '4473e6dd7e1d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('library',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('book_id', postgresql.UUID(), nullable=False),
    sa.Column('user_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('book_id', 'user_id'),
    sa.UniqueConstraint('id')
    )
    op.create_unique_constraint(None, 'book_roles', ['id'])
    op.create_unique_constraint(None, 'books', ['id'])
    op.create_unique_constraint(None, 'constraints', ['id'])
    op.create_unique_constraint(None, 'orders', ['id'])
    op.create_unique_constraint(None, 'presons', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'presons', type_='unique')
    op.drop_constraint(None, 'orders', type_='unique')
    op.drop_constraint(None, 'constraints', type_='unique')
    op.drop_constraint(None, 'books', type_='unique')
    op.drop_constraint(None, 'book_roles', type_='unique')
    op.drop_table('library')
    # ### end Alembic commands ###