"""empty message

Revision ID: 55fa97e01d02
Revises: cbbf16db46fa
Create Date: 2023-04-27 02:44:02.082874

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '55fa97e01d02'
down_revision = 'cbbf16db46fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('advertise',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('Content', sa.Text(), nullable=False),
    sa.Column('image_url', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contact',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('subject', sa.String(length=100), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
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

    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('search',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('result_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['result_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('concession_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('popcorn', sa.String(length=50), nullable=True),
    sa.Column('soda', sa.String(length=50), nullable=True),
    sa.Column('hotdog', sa.String(length=50), nullable=True),
    sa.Column('churros', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('ad')
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('room_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_booking_email'), ['email'], unique=True)
        batch_op.create_foreign_key(None, 'room', ['room_id'], ['id'])

    with op.batch_alter_table('social', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('social', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_booking_email'))
        batch_op.drop_column('room_id')
        batch_op.drop_column('email')

    op.create_table('ad',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('image_url', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='ad_pkey')
    )
    op.drop_table('concession_item')
    op.drop_table('search')
    op.drop_table('order')
    with op.batch_alter_table('forum', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_forum_timestamp'))

    op.drop_table('forum')
    op.drop_table('contact')
    op.drop_table('advertise')
    # ### end Alembic commands ###