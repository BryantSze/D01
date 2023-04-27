"""empty message

Revision ID: 782e2edfefd5
Revises: 3ef00ea14b4d
Create Date: 2023-04-26 13:51:52.218474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '782e2edfefd5'
down_revision = '3ef00ea14b4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('concession_item', schema=None) as batch_op:
        batch_op.drop_column('quantity')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('concession_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###