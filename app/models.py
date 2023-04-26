from datetime import datetime, timedelta, timezone
from hashlib import md5
from app import app, db, login
from flask_sqlalchemy import SQLAlchemy
import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, followers.c.followed_id == Post.user_id
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
        except:
            return None
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    director = db.Column(db.String(100))
    release_date = db.Column(db.Date)


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    bookings = db.relationship('Booking', backref='booking_room')

    def __repr__(self):
        return '<Room %r>' % self.id


class Seat(db.Model):
    __tablename__ = 'seat'
    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.String(1), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    room = db.relationship('Room', backref='seats')
    bookings = db.relationship('Booking', backref='seat_record')

    def __repr__(self):
        return '<Seat %r>' % self.id


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id'))
    room = db.relationship(
        'Room', backref='booking_history', foreign_keys=[room_id])
    cinema = db.relationship(
        'Cinema', backref='booking_history', foreign_keys=[cinema_id])
    users = db.relationship('User', backref='booking', foreign_keys=[user_id])
    seat = db.relationship(
        'Seat', backref='booking_history', foreign_keys=[seat_id])

    def __repr__(self):
        return '<Booking %r>' % self.id


class Cinema(db.Model):
    __tablename__ = 'cinema'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    bookings = db.relationship("Booking", back_populates="cinema")
    parent_cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id'))


class Showtime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)


class ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Advertise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Advertise {self.title}>'


class Social(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Social('{self.title}', '{self.date_posted}')"


class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"ContactMessage('{self.name}', '{self.email}', '{self.subject}')"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')

    user = db.relationship('User', backref='orders')

    concession_items = db.relationship('ConcessionItem', backref='order')

    def __repr__(self):
        return '<Order {}>'.format(self.id)


class ConcessionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    popcorn = db.Column(db.String(50))
    soda = db.Column(db.String(50))
    hotdog = db.Column(db.String(50))
    churros = db.Column(db.String(50))


def __repr__(self):
    return '<ConcessionItem id={}>'.format(self.id)


class Forum(db. Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db. Column(db. String(140))

    def __repr__(self):
        return '<Forum{}>'. format(self. body)


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    result_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Search {self.user_id} -> {self.result_id}>'
