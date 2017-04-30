"""
Initialize user app module which contains views to handle user functions.
"""
from flask import Blueprint
from app.common.logging_module import setup_logging

user_app = Blueprint('user_app', __name__)

# Setup the logger
user_app_logger = setup_logging(__name__, 'logs/user_app.log', 1000000, 5)

from app.user_app import errors, views
from app.models import Permission


@user_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
