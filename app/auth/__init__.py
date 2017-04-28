"""
Initialize authorization webapp module blue print and set logging mechanism.
"""

from app.common.loggingModule import setup_logging
from flask import Blueprint

auth = Blueprint('auth', __name__)

# Setup the logger
auth_logger = setup_logging(__name__, 'logs/auth.log', 1000000, 5)

from app.auth import views