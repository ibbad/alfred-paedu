"""
Module containing generic functions for Jinja2 Template.
"""

from flask import render_template, current_app, abort, request
from app.webapp import webapp, webapp_logger
from app.models import User


@webapp.route('/')
@webapp.route('/index')
def index():
    return render_template('index.html')


@webapp.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

"""
Helper functions for JINJA2 templates. These functions are used to performs
lightweight functionality inside JINJA2 template without providing full
object to the template.
"""


@webapp.add_app_template_global
def get_registrant(sub_id):
    """
    Returns the first name and last name of the subscriber whose id is provided.
    :param sub_id: ID of the subscriber whose first and last name is required.
    :return (firstname, lastname): String tuple
    """
    sub = Subscriber.objects(id=sub_id).first()
    if sub is not None:
        webapp_logger.debug('Returning subscriber %d name' % sub.id)
        return sub.first_name, sub.last_name
    else:
        webapp_logger.warning('Subscriber %d not found in database.' % sub_id)
        return ''


@webapp.add_app_template_global
def get_registrant_username(sub_id):
    """
    Returns the username of the subscriber whose id is provided.
    :param sub_id: ID of the subscriber whose first and last name is required.
    :return username: String.
    """
    sub = Subscriber.objects(id=sub_id).first()
    if sub is not None:
        webapp_logger.debug('Returning subscriber %d username to jinja2 '
                            'template.' % sub_id)
        return sub.username
    else:
        webapp_logger.warning('Subscriber %d not found in database.' % sub_id)
        return ''