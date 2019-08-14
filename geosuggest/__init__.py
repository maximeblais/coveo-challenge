from flask import Flask
from geosuggest.geodb import GeoDB
from .api.blueprints import base, suggestions
from .api.errors import InvalidQuery
from .config import *


def create_app(testing=False, additional_config=None):
    app = Flask(__name__, template_folder='templates')

    if testing:
        configuration = TestingConfig()
    elif app.config['ENV'] == 'development':
        configuration = DevelopmentConfig()
    else:
        configuration = ProductionConfig()

    app.config.from_object(configuration)

    if additional_config:
        app.config.from_mapping(additional_config)

    app.register_blueprint(base.bp)
    app.register_blueprint(suggestions.bp)

    return app
