from flask import Flask
from geosuggest.geodb import GeoDB
from .api.blueprints import base, suggestions
from .api.errors import InvalidQuery
from .config import *


def create_app(test_config=None):
    app = Flask(__name__, template_folder='templates')

    # Load appropriate config according to FLASK_ENV env var
    if app.config['ENV'] == 'development':
        configuration = DevelopmentConfig()
    elif app.config['ENV'] == 'testing':
        configuration = TestingConfig()
    else:
        configuration = ProductionConfig()

    app.config.from_object(configuration)

    # Override values with supplied test_config
    if test_config is not None:
        app.config.from_mapping(test_config)

    app.register_blueprint(base.bp)
    app.register_blueprint(suggestions.bp)

    return app
