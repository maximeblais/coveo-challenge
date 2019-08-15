from geosuggest import create_app
import pytest

# Fixture for an instance of our app in testing mode
@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


# Fixture for the Werkzeug test client of our app instance
@pytest.fixture
def client(app):
    return app.test_client()
