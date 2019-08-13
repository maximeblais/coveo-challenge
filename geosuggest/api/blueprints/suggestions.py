from flask import Blueprint, request, jsonify
from geopy import distance
from difflib import SequenceMatcher
from geosuggest.geodb import db, GeoRecord
from ..errors import InvalidQuery


bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


@bp.errorhandler(InvalidQuery)
def handle_invalid_query(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@bp.route('/', methods=['GET'])
def suggest():
    place = request.args.get('q')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if place is None:
        raise InvalidQuery("The 'q' (partial or full name) parameter must be present.")
    if (latitude or longitude) and (not latitude or not longitude):
        raise InvalidQuery("The 'latitude' and 'longitude' parameters must be used together.")

    if latitude or longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            raise InvalidQuery("The 'latitude' and 'longitude' parameters must be valid floating-point numbers")

    candidates = db.find_by_name(place)
    suggestions = to_weighted_results(place, candidates, latitude, longitude)

    suggestions = sorted(suggestions, key=lambda sugg: sugg['score'], reverse=True)

    return jsonify(suggestions=suggestions)


def to_weighted_results(place: str, candidates: [GeoRecord], latitude: float = None, longitude: float = None) -> [dict]:
    if len(candidates) == 0:
        return candidates

    evaluate_distance = True if latitude or longitude else False

    weights = {
        'name': 6,
        'nearness': 4,
    }

    suggestions = []

    for candidate in candidates:
        candidate_score = get_name_score(place, candidate, weights['name'])
        if evaluate_distance:
            candidate_score += get_nearness_score(latitude, longitude, candidate, weights['nearness'])
        else:
            candidate_score += weights['nearness']

        suggestions.append({**candidate.to_dict(simple=True), "score": candidate_score})

    return suggestions


def get_name_score(place: str, candidate: GeoRecord, weight) -> float:
    scores = [SequenceMatcher(a=place, b=candidate.name), SequenceMatcher(a=place, b=candidate.ascii_name)]

    return max([score.ratio() for score in scores]) * weight


def get_nearness_score(latitude, longitude, candidate, weight):
    canada_us_diameter = 6430  # approximate, in km

    position = (latitude, longitude)
    candidate_position = (candidate.latitude, candidate.longitude)
    distance_between = distance.distance(position, candidate_position).kilometers
    print(distance_between)
    score = weight - ((distance_between * weight) / canada_us_diameter)

    return score
