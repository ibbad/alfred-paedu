"""
Initialize activity application module containing views to handle adding new
activities, editing previous activities etc.
"""
from flask import Blueprint
from app.common.logging_module import setup_logging

activity_app = Blueprint('activity_app', __name__)

# setup logging
aa_logger = setup_logging(__name__, 'logs/activity_app.log', 1000000, 5)

from . import views, errors
from app.models import Permission

@activity_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
