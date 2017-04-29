"""
This module implements RestAPI calls for tokens api.
"""

import json
from flask import jsonify, request, g
from werkzeug.exceptions import BadRequest
from app.tokens_api_v1_0 import tokens_api, tokens_api_logger
from app.tokens_api_v1_0.authentication import login_exempt
from app.models import User
from app.api_errors import bad_request, unauthorized, custom_error


@tokens_api.route('/token', methods=['GET'])
def get_auth_token():
    """
    Generate an authentication token for the user. New token can only be
    obtained by using username and password, not authentication token.
    :return: authentication token with expiration in JSON format.
    """
    if g.current_user.is_anonymous or g.token_used:
        # g.token_used in the condition, so that users can not
        # use the previous token to generate a new one.
        tokens_api_logger.warning('User %d used token to get a new token.'
                                  % g.current_user.id)
        return unauthorized('invalid credentials provided for authentication '
                            'token generation.')
    tokens_api_logger.info('Authentication token successfully generated '
                           'for User %d' % g.current_user.id)
    return jsonify({
        'auth-token': g.current_user.generate_auth_token(expiration=3600),
        'expiration': 3600})


@tokens_api.route('/confirmation_token', methods=['GET'])
def get_confirmation_token():
    """
    Generate a confirmation token for the user. Using this token,
    user can confirm his/her account.
    :return: account confirmation token with expiration in JSON format.
    """
    if g.current_user.is_anonymous:
        tokens_api_logger.warning('Request to generated confirmation token from'
                                  ' unregistered user.')
        return unauthorized('invalid credentials used for confirmation token '
                            'generation.')
    tokens_api_logger.info('Confirmation token successfully generated for '
                           'user %d' % g.current_user.id)
    return jsonify({
        'conf_token': g.current_user.generate_confirmation_token(
            expiration=3600),
        'expiration': 3600}), 200


@tokens_api.route('/confirm/<confirmation_token>', methods=['POST'])
@login_exempt
def confirm_user(confirmation_token):
    """
    Use the confirmation token to confirm user account.
    :param confirmation_token: account confirmation token generated for the
    user.
    :return: json data for success, failure.
    """
    if User.verify_confirmation_token(confirmation_token):
        tokens_api_logger.info('User successfully confirmed using '
                               ' confirmation token')
        return jsonify({'success': 'User successfully confirmed'})
    tokens_api_logger.warning('Confirmation request using invalid token.')
    return bad_request('invalid token used for user confirmation')


@tokens_api.route('/login_change_token', methods=['GET'])
def get_login_change_token():
    """
    Generates a token to change login information (username/ email address) of
    the user. New username/email address is provided in json with the
    request. If the username/email already exists, no token is returned.
    :return: login information change token with expiration in JSON format.
    """
    try:
        request_data = json.loads(request.data)
        username_or_email = request_data.get('username') or \
            request_data.get('email')
        tokens_api_logger.info('Returning login change token for User %d'
                              % g.current_user.id)
        return jsonify({
            'login_change_token': g.current_user.generate_login_change_token(
                username_or_email=username_or_email,
                expiration=3600),
            'expiration': 3600}), 200
    except (BadRequest, AttributeError, ValueError):
        tokens_api_logger.warning('Invalid data provided with request to '
                                  'generate login change token by User %d'
                                  % g.current_user.id)
        return custom_error(error='Invalid json',
                            message='Invalid data provided with generate '
                                    'login change token',
                            status_code=425)


@tokens_api.route('/change_password_token', methods=['GET'])
@login_exempt
def get_change_password_token():
    """
    Generates a password change/reset token for the user. Provide
    username/email-address with request in JSON format to get the token.
    :return: password change/reset token with expiration in JSON format.
    """
    try:
        request_data = json.loads(request.data)
        username_or_email = request_data.get('username') or \
            request_data.get('email')
        tokens_api_logger.debug('login data retrieved from json data')
        user = User.objects(username=username_or_email).first() or \
            User.objects(email=username_or_email).first()
        if user is not None:
            tokens_api_logger.info('Returning password change token for'
                                   ' User %d' % user.id)
            return jsonify({
                'pwd_change_token': user.generate_pwd_reset_token(
                    expiration=3600),
                'expiration': 3600
            })
        tokens_api_logger.debug('User %d successfully retrieved from '
                                'database.' % user.id)
        tokens_api_logger.warning('Password change token requested for '
                                  'non-existing user.')
        return bad_request('User registered with given login '
                           'credentials %s not found.' % username_or_email)
    except (BadRequest, AttributeError, ValueError):
        tokens_api_logger.error('Invalid json data provided with request to '
                                'generate password change token.')
        return custom_error(error='Invalid json',
                            message='Invalid data provided',
                            status_code=425)


@tokens_api.route('/change_password/<change_password_token>', methods=['POST'])
@login_exempt
def change_user_password(change_password_token):
    """
    Sets the user password to the new password provided in JSON, using
    the reset password token generated for the user.
    :param change_password_token: Generated for user using different
    request.
    :param password: new password provided by user in JSON format.
    :return: Success if password changed, Error otherwise.
    """
    try:
        request_data = json.loads(request.data)
        new_password = request_data.get('password')
        user = User.verify_pwd_reset_token(change_password_token)
        if user is not None:
            tokens_api_logger.warning('Changing password for user with '
                                      'verified password change token.')
            user.change_password(pwd_reset_token=change_password_token,
                                  new_password=new_password)
            user.save()
            tokens_api_logger.info('User password successfully changed.')
            return jsonify({
                'success': 'Password changed successfully.',
            }), 200
        tokens_api_logger.warning('Invalid token used to change user '
                                  'password.')
        return bad_request('Invalid password reset token used to change '
                           'password.')
    except (BadRequest, AttributeError, ValueError):
        tokens_api_logger.warning('No new password provided with request to '
                                  'change password using password change '
                                  'token.')
        return custom_error(error='Invalid json',
                            message='No new password provided with change '
                                    'password request.',
                            status_code=425)
