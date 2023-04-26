from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, FileField,  SelectField, DateField, TimeField, EmailField , SelectMultipleField, IntegerField, validators
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, URL
from flask_babel import _, lazy_gettext as _l
from app.models import User ,Booking


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class BookingForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    movie = SelectField('Movie', choices=[('THE SUPER MARIO BROS. MOVIE', 'THE SUPER MARIO BROS. MOVIE'), ('Hachiko', 'Hachiko'), ('Over My Dead Body', 'Over My Dead Body'), ('RENFIELD', 'RENFIELD'), ('TO CATCH A KILLER', 'TO CATCH A KILLER'), ('Day off', 'Day off')], validators=[DataRequired()])
    price = SelectField('Price', choices=[('40', '40'), ('80', '80')], validators=[DataRequired()])
    seat =  IntegerField('Seat ID', validators=[DataRequired()])
    payment_method = SelectField('Payment methods', choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('paypal', 'PayPal')], validators=[DataRequired()])
    cinema = SelectField('Cinema ID', choices=[('16', '16'), ('20', '20'), ('14','14'), ('22','22'), ('10','10'), ('5','5'), ('12', '12'), ('21','21'), ('3','3'), ('6','6'), ('9','9'), ('19', '19')], validators=[DataRequired()])
    room =  SelectMultipleField('Room', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]) 
    submit = SubmitField('Book')
    
class SocialForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class AdvertiseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Image', validators=[DataRequired()])

class ConcessionForm(FlaskForm):
    popcorn = SelectField('Popcorn', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
                          validators=[DataRequired()])
    soda = SelectField('Soda', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
                       validators=[DataRequired()])
    soda_taste = SelectField('Soda Taste', choices=[('cola', 'cola'), ('sprite', 'sprite'), ('cream', 'cream'), ('sarsi', 'sarsi'), ('cream milk', 'cream milk')],
                       validators=[DataRequired()])
    hotdog = IntegerField('hotdog', validators=[DataRequired(), validators.NumberRange(min=0, max=10)])
    churros = IntegerField('churros', validators=[DataRequired(), validators.NumberRange(min=0, max=10)])
    submit = SubmitField('ConcessionItem')

