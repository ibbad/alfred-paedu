"""
Templates for forms to be used in user app module
"""

from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField, SelectField, \
    PasswordField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User
from helper.countries import get_country_list
from helper.regex_strings import POSTAL_CODE, USERNAME
from helper.strings import username_validation


class NameForm(Form):
    """
    Web form for updating subscriber name.
    """
    first_name = StringField('First name', validators=[Required])
    last_name = StringField('Last name', validators=[Required])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    """
    Web form for editing subscriber information.
    """
    # Get subscriber's personal information
    first_name = StringField('First name', validators=[Length(0, 64)])
    last_name = StringField('Last name', validators=[Length(0, 64)])
    company = StringField('Company name', validators=[Length(0, 64)])
    phone = StringField('Phone number', validators=[Length(0, 20)])

    # Get user's address information
    street = StringField('Street Address', validators=[Length(0, 255)])
    city = StringField('City', validators=[Length(0, 64)])
    postal_code = StringField('Postal Code',
                              validators=[Length(0, 20),
                                          Regexp(POSTAL_CODE)])
    state = StringField('State', validators=[Length(0, 50)])
    country = SelectField('Country', validators=[],
                          choices=get_country_list())
    submit = SubmitField('Submit')

    def validate_country(self, field):
        if field.data.lower() == 'code':
            raise ValidationError('Please choose a valid country')


class EditProfileAdminForm(Form):
    """
    Webform for editing user's profile from admin console. Gives more
    option to change the email address or username of the user as well.
    """
    username = StringField('Username',
                           validators=[Required,
                                       Length(1, 64),
                                       Regexp(USERNAME, 0,
                                              username_validation)
                                       ])
    email = StringField('Email', validators=[Required,
                                             Length(1, 64),
                                             Email()])
    confirmed = BooleanField('Confirmed')
    first_name = StringField('First name', validators=[Length(0, 64)])
    last_name = StringField('Last name', validators=[Length(0, 64)])
    company = StringField('Company name', validators=[Length(0, 64)])
    phone = StringField('Phone number', validators=[Length(0, 20)])

    # Edit user's address information
    street = StringField('Street Address', validators=[Required,
                                                       Length(0, 255)])
    city = StringField('City', validators=[Required,
                                           Length(0, 64)])
    postal_code = StringField('Postal Code',
                              validators=[Length(0, 20),
                                          Regexp(POSTAL_CODE)])
    state = StringField('State', validators=[Length(0, 50)])
    country = SelectField('Country', validators=[Required],
                          choices=get_country_list(), default='code')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_country(self, field):
        if field.data.lower() == 'code':
            raise ValidationError('Please choose a valid country')

    def validate_email(self, field):
        if field.data != self.user.email \
                and User.objects(email=field.data).first() is not None:
            raise ValidationError('Email address is already registered.')

    def validate_username(self, field):
        if field.data != self.user.username \
                and User.objects(username=field.data).first() is not None:
            raise ValidationError('Username already exists.')


class RegistrationForm(Form):
    """
    Web form for registration of a new user.
    """
    email = StringField('Email',
                        validators=[Required, Length(1, 64), Email()])
    username = StringField('Username',
                           validators=[Required,
                                       Length(1, 64),
                                       Regexp(USERNAME, 0,
                                              username_validation)
                                       ])
    password = PasswordField('Password',
                             validators=[Required,
                                         EqualTo('password2',
                                                 message='Password must match.')
                                         ])
    password2 = PasswordField('Confirm password',
                              validators=[Required])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.objects(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.objects(username=field.data).first():
            raise ValidationError('Username already exists.')
