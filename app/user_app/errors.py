"""
This module specifies the errors that will be used in case the requesting
function is unable to process the request.
"""

from flask import render_template, request, jsonify
from app.user_app import user_app


@user_app.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        response.message = e
        return response
    return render_template('errors/403.html', message=e), 403


@user_app.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'page not found'})
        response.status_code = 404
        response.message = e
        return response
    return render_template('errors/404.html', message=e), 404


@user_app.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 400
        response.message = e
        return response
    return render_template('errors/500.html', message=e), 500
