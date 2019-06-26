"""book entity model changed

Revision ID: 2b600c59e81c
Revises: ce77d7a00c62
Create Date: 2019-06-25 12:40:38.877280

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b600c59e81c'
down_revision = 'ce77d7a00c62'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('images', postgresql.ARRAY(postgresql.UUID()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'images')
    # ### end Alembic commands ###
