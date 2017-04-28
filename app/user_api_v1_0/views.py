"""
RestAPI for user model v1.0.
"""
from mongoengine import ValidationError
from flask import jsonify, request, g
from app.user_api_v1_0 import user_api, user_api_logger
from app.models import User
from app.user_api_v1_0.authentication import login_exempt
from app.api_errors import bad_request, custom_error, forbidden
from werkzeug.exceptions import BadRequest


@user_api.route('/count')
def user_count():
    count = User.objects().count()
    return jsonify({'users': count})


@user_api.route('/secret_resource')
def secret_resource():
    # FIXME: make a decorator for validating account confirmation
    if not g.current_user.confirmed:
        user_api_logger.warning("Invalid request to access secret resource by"
                                " unconfirmed User %d" % g.current_user.id)
        return forbidden('User not confirmed')
    return jsonify({'secret': 'You know the secret now'}), 200


@user_api.route('/<confirmation_token>', methods=['POST'])
def confirm_user(confirmation_token):
    """
    Confirm the user using confirmation token generated for the
    user.
    :param confirmation_token: confirmation token generated using a separate
    request.
    """
    if not g.current_user.confirm(confirmation_token=confirmation_token):
        user_api_logger.warning("Invalid token used by User %d to "
                                "confirm." % g.current_user.id)
        return bad_request('Invalid confirmation token')
    user_api_logger.info("User %d successfully confirmed using "
                         "confirmation token" % g.current_user.id)
    return jsonify({'success': 'user confirmed successfully'}), 200


@user_api.route('/change_login/<login_change_token>', methods=['POST'])
def change_user_login(login_change_token):
    """
    Changes user login information i.e. username/email-address using the
    login change token generated for the user.
    :param login_change_token:
    """
    sub = g.current_user
    if not sub.change_login(login_change_token):
        user_api_logger.warning("Bad token used by User %d to change "
                                "login." % g.current_user.id)
        return bad_request('Invalid change login token')
    user_api_logger.info("User %d login changed successfully by using "
                         "token" % g.current_user.id)
    return jsonify({'status': 'success',
                    'username': g.current_user.username,
                    'email': g.current_user.email}), 200


@user_api.route('/<int:user_id>')
def get_user(user_id):
    """
    Get user information using his id.
    :param user_id: user id (integer)
    :return: json object containing user information.
    """
    sub = User.objects(id=user_id).first()
    if sub is not None:
        user_api_logger.info('Returning user %d information upon to '
                             'user %d' % (user_id, g.current_user.id))
        return jsonify(sub.to_json()), 200
    user_api_logger.warning('User %d requested information of '
                            'non-existing user.' % g.currrent_user.id)
    return custom_error(error='User not found',
                        message='No user found with given id',
                        statuscode=404)


@user_api.route('/update_address', methods=['PUT'])
def update_address():
    """
    Updates the address of user using the JSON data posted with request.
    :param : user address data in JSON format.
    """
    try:
        request_data = request.get_json()
    except BadRequest:
        user_api_logger.error('User %d provided invalid json data '
                              'provided with request to update user '
                              'address.' % g.current_user.id)
        return custom_error(error='Invalid json',
                            message='Invalid data provided',
                            statuscode=425)
    try:
        sub = g.current_user
        for key in sub.address.to_json():
            sub.address[key] = request_data.get(key)
        sub.save()
        user_api_logger.info('User %d update request successfully.' %
                     g.current_user.id)
        return jsonify({'success': 'Address updated successfully'}), 200

    except AttributeError:
        user_api_logger.error('Invalid json data provided by user %d '
                              'for updating address' % g.current_user.id)
        return custom_error(error='Invalid data',
                            message='Invalid json data provided',
                            statuscode=425)
    except Exception as e:
        user_api_logger.error('Unable to update user address. Error '
                              '%s' % e.message)
        return custom_error(error='Server error',
                            message='Unable to update address information.',
                            statuscode=500)


@user_api.route('/update', methods=['POST'])
def update_user_from_json_data():
    """
    Updates the user information including personal information as well as
    address information, posted as JSON data with the request.
    :param : JSON data containing user information.
    """
    try:
        request_data = request.get_json()
    except BadRequest:
        user_api_logger.error('User %d provided invalid json data '
                              'provided with request to update user '
                              'information.' % g.current_user.id)
        return custom_error(error='Invalid json',
                            message='Invalid data provided',
                            statuscode=425)
    try:
        sub = g.current_user
        sub.update_from_json(request_data)
        sub.save()
        user_api_logger.info('User %d data updated upon client request.' %
                            g.current_user.id)
        return jsonify({'success': 'user information updated successfully'}), \
            200

    except AttributeError:
        user_api_logger.error('Invalid json data provided by user %d '
                              'for securebox registration' %
                              g.current_user.id)
        return custom_error(error='Invalid data',
                            message='Invalid json data provided',
                            statuscode=425)
    except Exception as e:
        user_api_logger.error('Unable to change device registration. Error '
                              '%s' % e.message)
        return custom_error(error='Server error',
                            message='Unable to change device registration.',
                            statuscode=500)


@user_api.route('/register', methods=['POST'])
@login_exempt
def register_user():
    """
    Register a new user using the data posted with the request.
    :param : JSON data containing user information.
    """
    try:
        request_data = request.get_json()
    except BadRequest:
        user_api_logger.error('Invalid json data provided with request to '
                              'register new user ' % g.current_user.id)
        return custom_error(error='Invalid json',
                            message='Invalid data provided',
                            statuscode=425)
    try:
        username = request_data.get('username')
        email = request_data.get('email')

        if User.objects(username=username).first() is not None:
            user_api_logger.warning('Request to register user with '
                                    'duplicate username.')
            return bad_request('Username is not unique.')
        if User.objects(email=email).first() is not None:
            user_api_logger.warning('Request to register user with '
                                    'duplicate email address.')
            return bad_request('Email address is already registered.')

        user = User(username=username, email=email)
        user_api_logger.info('New user successfully registered with '
                             'username:%s and email:%s' % (username, email))
        if request.json.get('password') is None:
            user_api_logger.error('No password provided with request to '
                                  'register new user.')
            return bad_request('No password provided for new user')

        user.set_password(request_data.get('password'))
        user.update_from_json(json_data=request_data)
        user_api_logger.info('User data successfully updated.')
        user.save()
        user_api_logger.info('New user %d registered successfully.' %
                             user.id)
        return jsonify({'success': 'Registration successful'}), 201

    except ValidationError as e:
        user_api_logger.error('User registration failed due to error %s' %
                              e.message)
        return bad_request('Invalid data provided for user registration. '
                           'Invalid username, email.')
    except AttributeError:
        user_api_logger.error('Invalid json data provided by user %d '
                              'for user registration' %
                              g.current_user.id)
        return custom_error(error='Invalid data',
                            message='Invalid json data provided',
                            statuscode=425)
    except Exception as e:
        user_api_logger.error('Unable to register user. Error %s' % e.message)
        return custom_error(error='Server error',
                            message='Unable to change register user.',
                            statuscode=500)
