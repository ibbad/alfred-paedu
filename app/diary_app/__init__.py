"""
Initialize diary application module containing views to handle adding new
diaries, editing previous diaries etc.
"""
from flask import Blueprint
from app.common.logging_module import setup_logging

diary_app = Blueprint('diary_app', __name__)

# setup logging
da_logger = setup_logging(__name__, 'logs/diary_app.log', 1000000, 5)

from . import views, errors
from app.models import Permission

@diary_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
