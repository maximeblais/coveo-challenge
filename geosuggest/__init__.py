import os
import json
from flask import Flask
from geosuggest.geodb import GeoDB

db = GeoDB(file_path=os.path.dirname(os.path.abspath(__file__)) + '/data/cities_canada-usa.tsv', csv_dialect='excel-tab')


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    # If we are in a test scenario, we will be passed a test_config. If not, simply use the instance config.
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    return app
