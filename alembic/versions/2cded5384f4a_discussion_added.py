"""discussion added

Revision ID: 2cded5384f4a
Revises: f242443e38c7
Create Date: 2019-10-13 17:09:13.024402

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2cded5384f4a'
down_revision = 'f242443e38c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('discussion_groups',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('image', postgresql.UUID(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('discussion_members',
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('modification_date', sa.Integer(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('modifier', sa.String(), nullable=True),
    sa.Column('group_id', postgresql.UUID(), nullable=False),
    sa.Column('person_id', postgresql.UUID(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['discussion_groups.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('group_id', 'person_id'),
    sa.UniqueConstraint('id')
    )
    op.create_unique_constraint(None, 'group_users', ['group_id', 'user_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'group_users', type_='unique')
    op.drop_table('discussion_members')
    op.drop_table('discussion_groups')
    # ### end Alembic commands ###
