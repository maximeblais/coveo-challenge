from flask import Flask
from geosuggest.geodb import GeoDB
from .api.blueprints import base, suggestions
from .api.errors import InvalidQuery
from .config import *


# Create our Flask app instance
def create_app(testing=False, additional_config=None):
    app = Flask(__name__, template_folder='templates')

    # Instantiate config based on environment clues
    if testing:
        configuration = TestingConfig()
    elif app.config['ENV'] == 'development':
        configuration = DevelopmentConfig()
    else:
        configuration = ProductionConfig()

    app.config.from_object(configuration)

    # Configure extra config parameters
    if additional_config:
        app.config.from_mapping(additional_config)

    # Register our API blueprints
    app.register_blueprint(base.bp)
    app.register_blueprint(suggestions.bp)

    return app
