"""
Initialize posts module which contains views to handle posts and comments
section.
"""
from flask import Blueprint

posts_app = Blueprint('posts_app', __name__)

from . import views, errors
from ..models import Permission

@posts_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)