"""from_editor field added to book

Revision ID: 249a146cd508
Revises: 51f0532a0074
Create Date: 2019-07-20 14:02:58.050726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '249a146cd508'
down_revision = '51f0532a0074'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('from_editor', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'follows', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'follows', type_='unique')
    op.drop_column('books', 'from_editor')
    # ### end Alembic commands ###
