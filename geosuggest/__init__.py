from flask import Flask
from geosuggest.geodb import GeoDB
from .api.blueprints import base, suggestions
from .api.errors import InvalidQuery


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    # If we are in a test scenario, we will be passed a test_config. If not, simply use the instance config.
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.register_blueprint(base.bp)
    app.register_blueprint(suggestions.bp)

    return app
