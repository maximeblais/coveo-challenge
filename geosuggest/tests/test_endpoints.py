# Utility function to test if a response object represents a response to an invalid query
def is_invalid(response, is_json=False):

    if is_json:
        json = response.get_json()
        return json.get('message') and json.get('status_code') != 200
    else:
        return response.status_code != 200


# Verify we get a response on our index
def test_index(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200


# Verify that we dectect and handle an empty query properly
def test_invalid_query_empty(client):
    response = client.get('/suggestions', follow_redirects=True)
    assert is_invalid(response, is_json=True)


# Verify the handling of a query with only latitude specified, without longitude
def test_invalid_query_q_lat_only(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': -50
    }

    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert is_invalid(response, is_json=True)


# Verify a valid query with the q parameter only
def test_valid_query_q_only(client):
    params = {
        'q': 'Sherbrooke'
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert not is_invalid(response, is_json=True)


# Verify a valid query with q, latitude and longitude
def test_valid_query_q_lat_lon(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': 10,
        'longitude': 10
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert not is_invalid(response, is_json=True)


# Verify a valid query with all parameters
def test_valid_query_q_lat_lon_viz(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': 10.43,
        'longitude': 102.3,
        'visualize': True
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert not is_invalid(response)
    assert b'div id="map"' in response.data


# Verify the handling of lat/lon parameters which are not convertible to float
def test_invalid_query_lat_lon_not_float(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': 'str',
        'longitude': 'str'
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert is_invalid(response, is_json=True)


# Verify the handling of lat/lon parameters that are not within bounds
def test_invalid_query_lat_lon_invalid_values(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': -1000,
        'longitude': 1000
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert is_invalid(response, is_json=True)


# Verify the handling of an invalid 'visualize' parameter value
def test_invalid_query_viz_not_valid_option(client):
    params = {
        'q': 'Sherbrooke',
        'visualize': 'wrong_option'
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert is_invalid(response, is_json=True)


# Verify that we recognize a falsey value in the 'visualize' parameter
def test_valid_query_viz_false_value(client):
    params = {
        'q': 'Sherbrooke',
        'visualize': '0'
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert not is_invalid(response, is_json=True)
