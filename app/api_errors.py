"""
Modified error responses for RestAPI.
"""

from flask import jsonify
from app.exceptions import ValidationError


def not_found(message="Requested resource not found"):
    """
    Generates json response for requests for a resource not found.
    :param message: error message sent to the user.
    :return: json response, HTTP status code: 404
    """
    response = jsonify({'error': 'not_found',
                        'message': message})
    response.status_code = 404
    return response


def bad_request(message=None):
    """
    Generates json response for incoming request with bad/no data.
    :param message: error message sent to the user.
    :return: json response, HTTP status code: 400
    """
    response = jsonify({'error': 'bad_request',
                        'message': message})
    response.status_code = 400
    return response


def unauthorized(message=None):
    """
    Generates a json response for the unauthorized user tries to access the
    resource.
    :param message: error message sent to the user.
    :return: json-response, HTTP status code: 401
    """
    response = jsonify({'status': 401,
                        'error': 'unauthorized',
                        'message': message})
    response.status_code = 401
    return response


def forbidden(message=None):
    """
    Generates a json response for user who tries to access resource with no
    permission.
    :param message: error message sent to the user
    :return: json-response, HTTP status code: 403
    """
    response = jsonify({'error': 'forbidden',
                        'message': message})
    response.status_code = 403
    return response


def expired_token(message=None):
    """
    Returns the error in case the token is expired.
    :param message:
    :return: json response, error_messgae, HTTP Status code: 400
    """
    response = jsonify({'error': 'Invalid token',
                        'message': message})
    response.status_code = 400
    return response


def custom_error(error, message, status_code):
    """
    Generates json response for incoming request with bad/no data.
    :param message: error message sent to the user.
    :param error: error description
    :param status_code: HTTP status code to be returned.
    :return: json response
    """
    response = jsonify({'error': error,
                        'message': message})
    response.status_code = status_code
    return response


def validation_error(message, statuscode=400):
    """
    Returns the custom message with given status code incase of validation
    error.
    :param message: error message to be returned to requesting entity.
    :param statuscode: status code returned with the request.
    :return json_response, HTTP status code: 500
    """
    response = jsonify({'error': 'Validation error',
                        'message': message})
    response.status_code = statuscode
    return response

from app.user_api_v1_0 import user_api

@user_api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
