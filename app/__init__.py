"""
Initialize the blueprint for Application api v1.0
"""
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from config import config
from app.decorators import timeout

db = MongoEngine()
moment = Moment()
bootstrap = Bootstrap()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth_webapp.login'

# if it takes more than 10 seconds to setup application, raise an alarm
# Indicates failure to connect to MongoDB while testing.


@timeout(10)
def create_app(config_name):
    """
    Application Factory to initialize the Flask application.
    :param config_name: configuration running for the application.
    :return: application instance
    """
    app = Flask(__name__, static_folder='static', static_url_path='')

    # Load configuration
    # FIXME: Configuration loading issue.
    # app.config.from_object('config.{}'.format(TestingConfig))
    app.config.from_object(config[config_name])

    # Initialize the application
    config[config_name].init_app(app)

    # setup the plugins
    # FIXME: check if mongod is running before launching the app.
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app, add_context_processor=True)
    bootstrap.init_app(app)
    csrf.init_app(app)

    from app.webapp import webapp as webapp_blueprint
    app.register_blueprint(webapp_blueprint)

    # Register user_app blueprint
    from app.user_app import user_app as user_app_blueprint
    app.register_blueprint(user_app_blueprint,
                           url_prefix='/user')
    

    return app
