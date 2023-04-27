"""empty message

Revision ID: 3ef00ea14b4d
Revises: 0df98d2850af
Create Date: 2023-04-26 13:51:37.260190

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ef00ea14b4d'
down_revision = '0df98d2850af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('concession_item', schema=None) as batch_op:
        batch_op.drop_column('size')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('concession_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size', sa.VARCHAR(length=10), autoincrement=False, nullable=True))

    # ### end Alembic commands ###