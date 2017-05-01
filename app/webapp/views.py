"""
Module containing generic functions for Jinja2 Template.
"""

from flask import render_template, current_app, abort, request
from app.webapp import webapp, webapp_logger
from app.models import User, Comment


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
def get_fullname_from_id(user_id):
    """
    Returns the first name and last name of the subscriber whose id is provided.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return (firstname, lastname): String tuple
    """
    user = User.objects(id=user_id).first()
    if user is not None:
        webapp_logger.debug('Returning subscriber %d name' % user.id)
        return user.first_name, user.last_name
    else:
        webapp_logger.warning('Subscriber %d not found in database.' % user_id)
        return ''


@webapp.add_app_template_global
def get_username_from_id(user_id):
    """
    Returns the username of the subscriber whose id is provided.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return username: String.
    """
    user = User.objects(id=user_id).first()
    if user_id is not None:
        webapp_logger.debug('Returning user %d username to jinja2 '
                            'template.' % user.id)
        return user.username
    else:
        webapp_logger.warning('User %d not found in database.' % user_id)
        return ''


@webapp.add_app_template_global
def get_post_comment_count(post_id):
    """
    Returns the count for comments on given post.
    :param user_id: ID of the subscriber whose first and last name is required.
    :return username: String.
    """
    return Comment.objects(c_type=current_app.config["COMMENT_TYPE"][
        "POST"], post_id=post_id).count()