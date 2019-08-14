def is_invalid(response, is_json=False):

    if is_json:
        json = response.get_json()
        return json.get('message') and json.get('status_code') != 200
    else:
        return response.status_code != 200


def test_index(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200


def test_invalid_query_empty(client):
    response = client.get('/suggestions', follow_redirects=True)
    assert is_invalid(response, is_json=True)


def test_invalid_query_q_lat_only(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': -50
    }

    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert is_invalid(response, is_json=True)


def test_valid_query_q_only(client):
    params = {
        'q': 'Sherbrooke'
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert not is_invalid(response, is_json=True)


def test_valid_query_q_lat_lon(client):
    params = {
        'q': 'Sherbrooke',
        'latitude': 10,
        'longitude': 10
    }
    response = client.get('/suggestions', query_string=params, follow_redirects=True)
    assert not is_invalid(response, is_json=True)


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

