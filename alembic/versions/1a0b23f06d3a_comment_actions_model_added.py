"""comment-actions model added

Revision ID: 1a0b23f06d3a
Revises: e1b25e8a67a8
Create Date: 2019-07-17 18:20:38.390577

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a0b23f06d3a'
down_revision = 'e1b25e8a67a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comments', 'report')
    op.drop_column('comments', 'helpful')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('comments', sa.Column('helpful', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('report', postgresql.ENUM('Personal', 'Invalid_Content', name='reportcomment'), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
