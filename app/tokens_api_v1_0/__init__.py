"""
Initialize the blueprint for restAPI for token generation and authentication
v1.0.
"""

from app.common.logging_module import setup_logging
from flask import Blueprint

tokens_api = Blueprint('tokens_api', __name__)


# Setup the logger
tokens_api_logger = setup_logging(__name__, 'logs/tokens_api.log', 10000000, 5)


from app.tokens_api_v_1_0 import authentication, views
