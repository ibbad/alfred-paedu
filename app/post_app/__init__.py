"""
Initialize posts module which contains views to handle posts and comments
section.
"""
from flask import Blueprint
from app.common.logging_module import setup_logging

post_app = Blueprint('post_app', __name__)

# Setup the logger
pa_logger = setup_logging(__name__, 'logs/post_app.log', 1000000, 5)

from . import views, errors
from ..models import Permission


@post_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
