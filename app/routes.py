from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, session, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, BookingForm, SocialForm, AdvertiseForm, ContactForm
from app.models import User, Post, Booking ,Seat, Social, Cinema, Contact
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = BookingForm()
    if form.validate_on_submit():
        booking = Booking(movie=form.movie.data, time=form.time.data, price=form.price.data)
        db.session.add(booking)
        db.session.commit()
        for row in range(1, 11):
            for number in range(1, 11):
                seat = Seat(row=row, number=number, booking=booking)
                db.session.add(seat)
        db.session.commit()
        flash('Booking created successfully!')
        return redirect(url_for('main_bp.index'))
    return render_template('index.html.j2', form=form)


@app.route('/index', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=('home'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html.j2', title=_('Register'), form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('user.html.j2', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title=_('Edit Profile'),
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))

@app.route('/room/<int:room_id>')
def select_seats(room_id):
    # display a list of available seats for the selected room
    room = Room.query.get(room_id)
    seats = Seat.query.filter_by(room_id=room_id, available=True).all()
    return render_template('select_seats.html', room=room, seats=seats)


@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm(request.form)
    if form.validate_on_submit():
        # Query the database for the user
        user = User.query.filter_by(username=form.username.data).first()
        seat = Seat.query.get(form.seat.data)
        cinema = Cinema.query.get(form.cinema.data)

        booking = Booking(
            movie=form.movie.data,
            price=form.price.data,
            payment_method=form.payment_method.data,
            user=user,
            seat=seat,
            cinema=cinema
        )
        db.session.add(booking)
        db.session.commit()

        # Store the booking ID in the session
        session['booking_id'] = booking.id

        # Redirect to the success page after booking is successful
        return redirect(url_for('success'))

    return render_template('tickets.html.j2', title=_('Book'), form=form)

@app.route('/success')
def success():
    # Retrieve the booking data from the session
    booking_data = session.pop('booking_data', None)
    if not booking_data:
        # Redirect to the booking page if there is no booking data in the session
        return redirect(url_for('book'))
    return render_template('success.html.j2', booking_data=booking_data)






@app.route('/user/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html.j2', user=user, posts=posts)
    
@app.route('/cinema')
def cinema_location():
    return render_template('Cinema Location.html.j2')

@app.route('/<region>/cinemas/<int:cinemasid>')
def cinemas(region, cinemasid):
    # Logic to retrieve cinema data based on cinemasid and region
    # ...

    # Render the template for the specified cinema and region
    template_path = 'Cinemas/{region}/cinemasid={cinemasid}.html.j2'.format(region=region, cinemasid=cinemasid)
    return render_template(template_path)


@app.route('/cinema-details', endpoint='cinema_details')
def cinema_details():
    address = '123 Main St, Hong Kong'
    phone = '123-456-7890'
    email = 'info@cinema.com.hk'
    website = 'https://www.cinema.com.hk'
    return render_template('Cinema Location.html.j2', address=address, phone=phone, email=email, website=website)

@app.route('/ad/create', methods=['GET', 'POST'])
def create_ad():
    form = AdForm()
    if form.validate_on_submit():
        ad = Ad(title=form.title.data, description=form.description.data, image_url=form.image_url.data)
        db.session.add(ad)
        db.session.commit()
        ads = Ad.query.order_by(Ad.created_at.desc()).all()
        return redirect(url_for('index'))
    return render_template('create_ad.html.j2', form=form, ads=ads)


@app.route('/advertise', methods=['GET', 'POST'])
def advertise():
    form = AdvertiseForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        image = form.image.data
        return render_template('advertise.html.j2', form=form, success=True)
    return render_template('advertise.html.j2', form=form)


@app.route('/social/create', methods=['GET', 'POST'])
def create_social():
    form = SocialForm()
    if form.validate_on_submit():
        social = Social(title=form.title.data, content=form.content.data)
        db.session.add(social)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_social.html.j2', form=form)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(name=form.name.data, email=form.email.data, subject=form.subject.data, message=form.message.data)
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contactus.html.j2', form=form)

@app.route('/mario')
def mario():
    return render_template('mario.html.j2')

@app.route('/dog')
def dog():
    return render_template('dog.html.j2')

@app.route('/dead')
def dead():
    return render_template('dead.html.j2')

@app.route('/renfield')
def renfield():
    return render_template('renfield.html.j2')

