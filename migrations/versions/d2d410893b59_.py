"""empty message

Revision ID: d2d410893b59
Revises: cbbf16db46fa
Create Date: 2023-04-27 02:02:36.140941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2d410893b59'
down_revision = 'cbbf16db46fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('forum',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('forum', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_forum_timestamp'), ['timestamp'], unique=False)

    op.create_table('search',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('result_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['result_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('search')
    with op.batch_alter_table('forum', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_forum_timestamp'))

    op.drop_table('forum')
    # ### end Alembic commands ###
