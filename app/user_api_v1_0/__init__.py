"""
Initialize the blueprint for User module RestAPI v1.0
"""
from flask import Blueprint

user_api = Blueprint('user_api', __name__)

# Setup the logger
import logging
from logging.handlers import RotatingFileHandler

user_api_logger = logging.getLogger(__name__)
user_api_logger.setLevel(logging.INFO)

# Formatter for logs.
user_api_log_format = logging.Formatter('%(asctime)s - %(name)s - '
                                        '%(levelname)s - %(message)s')

# Setup FileHandler for the logs.
user_api_log_fh = RotatingFileHandler('logs/user_api.log',
                                      maxBytes=1000000,
                                      backupCount=5)
user_api_log_fh.setLevel(logging.INFO)
user_api_log_fh.setFormatter(user_api_log_format)

# Setup StreamHandler for important logs.
user_api_log_stream = logging.StreamHandler()
user_api_log_stream.setLevel(logging.ERROR)

# Add handlers to the logger.
user_api_logger.addHandler(user_api_log_fh)
user_api_logger.addHandler(user_api_log_stream)

from app.user_api_v1_0 import authentication, views