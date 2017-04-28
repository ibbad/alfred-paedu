"""
This module implements custom validators for different fields in forms used
in web application development.
"""

from wtforms import ValidationError
from app.models import User


def check_credential_duplication():
    """
    Custom validator implemented as decorator for checking if
    email address/ username provided is already attached to another user.
    :return:
    """
    message = 'Invalid username/email address.'

    def _validate_credential(form, field):
        user = User.objects(email=field.data).first() or \
              User.objects(username=field.data).first()
        if user is None:
            raise ValidationError(message)

    return _validate_credential


def check_email_duplication():
    """
    Custom validator implemented as decorator for checking if
    email address provided is already attached to another user.
    :return:
    """
    message = 'Email address already exists.'

    def _check_email_duplication(form, field):
        if User.objects(email=field.data).first() is not None:
            raise ValidationError(message)

    return _check_email_duplication


def check_username_duplication():
    """
    Custom validator implemented as decorator for checking if given
    username is already registered by another user.
    :return:
    """
    message = 'Username is already registered.'

    def _check_username_duplication(form, field):
        if User.objects(username=field.data).first() is not None:
            raise ValidationError(message)

    return _check_username_duplication


def country_validation():
    """
    Custom validation for ensuring that subscriber chooses a valid country
    while registration or updating information.
    :return:
    """
    message = 'Please choose a valid country.'

    def _validate_country(form, field):
        if field.data.lower() == 'code':
            raise ValidationError(message)

    return _validate_country
