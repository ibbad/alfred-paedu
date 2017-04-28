from flask import Blueprint

webapp = Blueprint('webapp', __name__)

# Setup the logger
import logging
from logging.handlers import RotatingFileHandler

webapp_logger = logging.getLogger(__name__)
webapp_logger.setLevel(logging.INFO)

# Formatter for logs.
webapp_log_format = logging.Formatter('%(asctime)s - %(name)s - '
                                      '%(levelname)s - %(message)s')

# Setup FileHandler for the logs.
webapp_log_fh = RotatingFileHandler('logs/subscriber_api.log',
                                    maxBytes=1000000,
                                    backupCount=5)
webapp_log_fh.setLevel(logging.INFO)
webapp_log_fh.setFormatter(webapp_log_format)

# Setup StreamHandler for important logs.
webapp_log_stream = logging.StreamHandler()
webapp_log_stream.setLevel(logging.ERROR)

# Add handlers to the logger.
webapp_logger.addHandler(webapp_log_fh)
webapp_logger.addHandler(webapp_log_stream)

from app.webapp import errors, views