from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, session, g
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, BookingForm, SocialForm, AdvertiseForm, ContactForm, ConcessionForm
from app.models import User, Post, Booking ,Seat, Social, Cinema, Contact, Order, ConcessionItem
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('home', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('home', page=posts.prev_num) if posts.prev_num else None
    return render_template('home.html.j2', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


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

@app.route('/seatplan')
def seatplan():
    # display a list of available seats for the selected room
    return render_template('seatplan.html.j2')


@app.route('/book', methods=['GET', 'POST'])
def book():
    form = BookingForm(request.form)
    if form.validate_on_submit():
        # Query the database for the user
        user = User.query.filter_by(username=form.username.data).first()
        seat = Seat.query.get(form.seat.data)
        cinema = Cinema.query.get(form.cinema.data)
        room = Room.query.get(form.room.data)

        booking = Booking(
            movie=form.movie.data,
            email=form.email.data,
            price=form.price.data,
            payment_method=form.payment_method.data,
            user=user,
            seat=seat,
            cinema=cinema,
            room=room
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
    # Retrieve the booking ID from the session
    booking_id = session.pop('booking_id', None)
    if not booking_id:
        # Redirect to the booking page if there is no booking ID in the session
        return redirect(url_for('book'))

    # Retrieve the booking data from the database
    booking = Booking.query.get(booking_id)
    booking_data = {
        'movie': booking.movie ,
        'email': booking.email,
        'price': booking.price,
        'payment_method': booking.payment_method,
        'user': booking.user.username if booking.user else 'User',
        'seat': booking.seat.seat if booking.seat else '11',
        'cinema': booking.cinema.cinema if booking.cinema else '1',
        'room': booking.room.room if booking.room else '1',
        
    }

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

@app.route('/concession', methods=['GET', 'POST'])
@login_required     
def concession():
    form = ConcessionForm(request.form)
    if form.validate_on_submit():
        # Create a new order for the current user
        order = Order(user_id=current_user.id, status='pending')
        db.session.add(order)
        db.session.commit()

        # Create concession items for the order
        concession = ConcessionItem(
            order_id=order.id,
            popcorn=form.popcorn.data,
            soda=form.soda.data,
            hotdog=form.hotdog.data,
            churros=form.churros.data
        )
        db.session.add(concession)

        # Commit the changes to the database
        db.session.commit()

        # Store the concession ID in the session
        session['concession_id'] = concession.id

        # Debug statement to print out form data
        print('Form data:', form.popcorn.data, form.soda.data, form.hotdog.data, form.churros.data)

        return redirect(url_for('concession_success', concession_id=concession.id))
    
    return render_template('concession.html.j2', title='Concession', form=form)

 
@app.route('/concession/success/<int:concession_id>')
@login_required
def concession_success(concession_id):
    concession = ConcessionItem.query.get(concession_id)
    if not concession:
        # Redirect to the concession page if there is no concession with the given ID
        return redirect(url_for('concession'))

    # Pass the concession item data to the template
    concession_data = {
        'popcorn': concession.popcorn,
        'soda': concession.soda,
        'hotdog': concession.hotdog,
        'churros': concession.churros
    }

    # Create a new instance of the ConcessionForm and pass it to the template
    form = ConcessionForm()
    return render_template('concession_success.html.j2', concession_data=concession_data, form=form)

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


@app.route('/killer')
def killer():
    return render_template('killer.html.j2')

@app.route('/dayoff')
def dayoff():
    return render_template('dayoff.html.j2')