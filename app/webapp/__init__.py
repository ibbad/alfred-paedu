from flask import Blueprint
from app.common.logging_module import setup_logging

webapp = Blueprint('webapp', __name__)

# Setup the logger
webapp_logger = setup_logging(__name__, 'logs/webapp.log', 1000000, 5)

from app.webapp import errors, views
