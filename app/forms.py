from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, FileField,  SelectField, DateField, TimeField, EmailField , SelectMultipleField
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
    price = SelectField('Price Special Tickets HKD40 Normal Tickets HKD80', choices=[('40', '40'), ('80', '80')], validators=[DataRequired()])
    seat =  StringField('Seat', validators=[DataRequired()])
    payment_method = SelectField('Payment methods', choices=[('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('paypal', 'PayPal')], validators=[DataRequired()])
    cinema = SelectField('Cinema', choices=[('16', 'MOViE MOViE Pacific Place (Admiralty)'), ('20', 'MOViE MOViE Cityplaza (Taikoo Shing)'), ('14','B+ cinema apm (Kwun Tong)'), ('22','B+ cinema MOKO (Mong Kok East)'), ('10','CINEMATHEQUE'), ('5','MONGKOK'), ('12', 'PALACE ifc'), ('21','PREMIERE ELEMENTS'), ('3','TSUEN WAN'), ('6','KWAI FONG'), ('9','KINGSWOOD'), ('19', 'MY CINEMA YOHO MALL')], validators=[DataRequired()])
    room =  SelectMultipleField('Room', choices=[('Room1', 'Room1'), ('Room2', 'Room2'), ('Room3', 'Room3'), ('Room4', 'Room4'), ('Room5', 'Room5')]) 
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