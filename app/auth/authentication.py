"""
Authentication module for Authentication RestAPI/ Webapp.
"""

from flask import g, request, current_app
from flask.ext.httpauth import HTTPBasicAuth
from app.models import Subscriber, AnonymousUser
from app.user_api_1_0 import api
from app.api_errors import unauthorized

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_username_or_token, password):
    # No email/username/token provided.
    if email_or_username_or_token == '':
        g.current_user = AnonymousUser
        return False

    # username/email-address used
    user = User.objects(email=email_or_username_or_token).first() \
        or user.objects(username=email_or_username_or_token).first()
    if subscriber is not None:
        g.current_user = subscriber
        g.token_used = False
        return user.verify_password(password)

    # token used
    g.current_user = Subscriber.verify_auth_token(email_or_username_or_token)
    g.token_used = True
    return g.current_user is not None


@auth.error_handler
def auth_error():
    return unauthorized('invalid credentials!')


def login_exempt(f):
    f.login_exempt = True
    return f

# dummy callable to execute the login_required logic
login_required_dummy_view = auth.login_required(lambda: None)


@api.before_request
def before_request():
    # make sure that endpoints are exempted from login
    # use split to handle blueprint static routes as well.
    if not request.endpoint or request.endpoint.rsplit('.', 1)[-1] == 'static':
        return

    view = current_app.view_functions[request.endpoint]

    if getattr(view, 'login_exempt', False):
        return

    return login_required_dummy_view()
