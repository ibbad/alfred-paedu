"""
Initialize the blueprint for User module RestAPI v1.0
"""
from flask import Blueprint
from app.common.logging_module import setup_logging

user_api = Blueprint('user_api', __name__)

# Setup the logger
user_api_logger = setup_logging(__name__, 'logs/user_api.log', 1000000, 5)

from app.user_api_v1_0 import authentication, views
