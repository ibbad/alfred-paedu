"""
Initialize web app portal for suggestion feature.
"""

from flask import Blueprint
from app.common.logging_module import setup_logging

sugg_app = Blueprint('sugg_app', __name__)

# Setup the logger
sa_logger = setup_logging(__name__, 'logs/sugg_app.log', 1000000, 5)

from . import views, errors
from app.models import Permission

@sugg_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)