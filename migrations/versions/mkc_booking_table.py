"""booking table

Revision ID: mkc
Revises: 
Create Date: 2023-4-19 03:17:42.131626

"""
from alembic import op
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

# revision identifiers, used by Alembic.
revision = 'mkc'
down_revision = None
branch_labels = None
depends_on = None

db = SQLAlchemy()

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)

    user = db.relationship('User', backref='bookings')
    seat = db.relationship('Seat', backref='bookings')

    def __repr__(self):
        return '<Booking %r>' % self.id
