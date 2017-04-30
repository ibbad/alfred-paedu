"""
This module describes the forms used in authentication web application.
"""

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo
from app.common.custom_validators import check_credential_duplication, \
    check_username_duplication, check_email_duplication


class LoginForm(Form):
    """
    User form for login using email or username.
    """
    username_or_email = StringField('Username or email address',
                                    validators=[InputRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')


class ChangePasswordForm(Form):
    """
    Web form for changing user password when user is logged in.
    """
    old_password = PasswordField('Old password', validators=[InputRequired()])
    password = PasswordField('New password',
                             validators=[InputRequired(),
                                         EqualTo('password2',
                                                 message='Passwords must match')
                                         ])
    password2 = PasswordField('Confirm new password',
                              validators=[InputRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
    """
    Web form for making a request for (forgotten or stolen etc.) password reset
    by the user.
    """
    username_or_email = StringField('Username or email address',
                                    validators=[InputRequired(),
                                                Length(1, 64)])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    """
    Web form for resetting password for user.
    """
    username_or_email = StringField('Username or email address',
                                    validators=[
                                        InputRequired(), Length(1, 64),
                                        check_credential_duplication()])
    password = PasswordField('New password',
                             validators=[InputRequired(),
                                         EqualTo('password2',
                                                 message='Passwords must match')
                                         ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Reset Password')


class PasswordChangeForm(Form):
    """
    Web form for changing password for user without using username/email.
    when user is not logged and uses a token to access this page.
    """
    password = PasswordField('New password',
                             validators=[InputRequired(),
                                         EqualTo('password2',
                                                 message='Passwords must match')
                                         ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Reset Password')


class ChangeUsernameForm(Form):
    """
    Web form for changing user login information i.e. username.
    """
    new_username = StringField('New username', validators=[
        InputRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores'), check_username_duplication()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update')


class ChangeEmailForm(Form):
    """
    Web form for changing user login information i.e. email.
    """
    new_email = StringField('New email',
                            validators=[InputRequired(), Length(1, 64),
                                        Email(), check_email_duplication()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update')

    # def validate_email(self, field):
    #     if User.objects(email=field.data).first() is not None:
    #         raise ValidationError('Email already registered.')


class ChangeLoginForm(Form):
    """
    Web form for changing user login information i.e. email or username.
    """
    username_or_email = StringField('New username or email',
                                    validators=[InputRequired(), Length(1, 64),
                                                check_credential_duplication()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update login information')


class ConfirmationForm(Form):
    """
    Web form for confirmation of user.
    """
    name = StringField('Real name')
    username = StringField('Username')
    email = StringField('Email address')
    submit = SubmitField('Confirm')


class ConfirmRegistrationForm(Form):
    """
    Web form for confirmation of user registration.
    """
    submit = SubmitField('Confirm')