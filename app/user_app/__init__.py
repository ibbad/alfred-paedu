from flask import Blueprint

user_app = Blueprint('user_app', __name__)

# Setup the logger
import logging
from logging.handlers import RotatingFileHandler

user_app_logger = logging.getLogger(__name__)
user_app_logger.setLevel(logging.INFO)

# Formatter for logs.
user_app_log_format = logging.Formatter('%(asctime)s - %(name)s - '
                                        '%(levelname)s - %(message)s')

# Setup FileHandler for the logs.
user_app_log_fh = RotatingFileHandler('logs/user_app.log',
                                      maxBytes=1000000,
                                      backupCount=5)
user_app_log_fh.setLevel(logging.INFO)
user_app_log_fh.setFormatter(user_app_log_format)

# Setup StreamHandler for important logs.
user_app_log_stream = logging.StreamHandler()
user_app_log_stream.setLevel(logging.ERROR)

# Add handlers to the logger.
user_app_logger.addHandler(user_app_log_fh)
user_app_logger.addHandler(user_app_log_stream)

from app.user_app import errors, views
from app.models import Permission


@user_app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)