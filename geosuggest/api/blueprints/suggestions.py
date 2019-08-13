from flask import Blueprint, request, jsonify
from geopy import distance
from difflib import SequenceMatcher
from geosuggest.geodb import db, GeoRecord
from ..errors import InvalidQuery


bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


# Handler for invalid queries
@bp.errorhandler(InvalidQuery)
def handle_invalid_query(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Main route for suggestions
# Required: q
# Optional: latitude & longitude
# Usage: GET /suggestions?q=<search_term>&latitude=<float>&longitude=<float>
@bp.route('/', methods=['GET'])
def suggest():
    # Get required and optional arguments from query
    place = request.args.get('q')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    # Validate query
    if place is None:
        raise InvalidQuery("The 'q' (partial or full name) parameter must be present.")
    if (latitude or longitude) and (not latitude or not longitude):
        raise InvalidQuery("The 'latitude' and 'longitude' parameters must be used together.")

    # Transform latitude and longitude to floats for easier handling
    if latitude or longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            raise InvalidQuery("The 'latitude' and 'longitude' parameters must be valid floating-point numbers")

    # Find potential candidates and calculate their score
    candidates = db.find_by_name(place)
    suggestions = to_weighted_results(place, candidates, latitude, longitude)

    # Order suggestions by score from highest to lowest
    suggestions = sorted(suggestions, key=lambda sugg: sugg['score'], reverse=True)

    return jsonify(suggestions=suggestions)


def to_weighted_results(place: str, candidates: [GeoRecord], latitude: float = None, longitude: float = None) -> [dict]:
    # If there are no potential candidates, return immediately (implicitly returning [])
    if len(candidates) == 0:
        return candidates

    evaluate_distance = True if latitude or longitude else False

    # Name similarity is given a weight of 60% of the candidate score, nearness 40%
    weights = {
        'name': 0.6,
        'nearness': 0.4,
    }

    suggestions = []

    # Evaluate each candidate score according to name similarity and nearness
    for candidate in candidates:
        candidate_score = get_name_score(place, candidate, weights['name'])
        if evaluate_distance:
            if candidate.latitude == latitude and candidate.longitude == longitude:
                candidate_score = 1
            else:
                candidate_score += get_nearness_score(latitude, longitude, candidate, weights['nearness'])
        else:
            candidate_score += weights['nearness']

        # Combine candidate and calculated score then append it to [suggestions]
        suggestions.append({**candidate.to_dict(simple=True), "score": candidate_score})

    return suggestions


def get_name_score(place: str, candidate: GeoRecord, weight) -> float:
    # Evaluate string similarity between user query and candidate's name and ascii_name
    scores = [SequenceMatcher(a=place, b=candidate.name), SequenceMatcher(a=place, b=candidate.ascii_name)]

    # Return the highest ratio of similarity, rebalanced on a scale of [0, weight]
    return max([score.ratio() for score in scores]) * weight


def get_nearness_score(latitude: float, longitude: float, candidate: GeoRecord, weight: float) -> float:
    canada_us_diameter = 6430  # approximate, in km

    # Evaluate distance between user supplied coordinates and candidate
    position = (latitude, longitude)
    candidate_position = (candidate.latitude, candidate.longitude)
    distance_between = distance.distance(position, candidate_position).kilometers
    # Translate from scale [0, canada_us_diameter] to [0, weight]
    score = weight - ((distance_between * weight) / canada_us_diameter)

    return score
