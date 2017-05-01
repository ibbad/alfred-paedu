import os
import json
from pprint import pprint
basedir = os.path.abspath(os.path.dirname(__file__))

from helper.helper_functions import generate_secret_key


class Config:
    """
    Key configurations parameters.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or generate_secret_key()
    SSL_DISABLE = False
    APP_ADMIN = 'admin@example.com'
    SEND_FILE_MAX_AGE_DEFAULT = 0       # Disable browser cache
    # WTF_CSRF_ENABLED = True
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 15
    COMMENT_TYPE = {
        "POST": 1,
        "ACTIVITY": 2
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Application configuration for development phase.
    """
    DEBUG = True
    MONGODB_DB = 'development_db'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017


class TestingConfig(Config):
    """
    Application configuration for testing phase.
    """
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MONGODB_DB = 'testing_db'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017



class ProductionConfig(Config):
    """
    Application configuration for production environment.
    """
    MONGODB_SETTINGS = {
        'db': 'production_db',
        'host': 'server_ip',
        'port': 27017,       # default =27017
        'username': os.environ.get('MONGODB_USERNAME') or 'username',
        'password': os.environ.get('MONGODB_PASSWORD') or 'password'
    }

    @classmethod
    def init_app(app):
        Config.init_app(app)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}