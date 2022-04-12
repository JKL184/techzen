"""empty message

Revision ID: de35430a904c
Revises: 6a627bd86cac
Create Date: 2022-04-12 02:54:41.642884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de35430a904c'
down_revision = '6a627bd86cac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('graphicalanalytics', sa.Column('interestrate', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('graphicalanalytics', 'interestrate')
    # ### end Alembic commands ###
