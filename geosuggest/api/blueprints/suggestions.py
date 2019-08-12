from flask import Blueprint, render_template, request, jsonify
from geopy import distance
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
    #suggestions = to_weighted_results(place, candidates, latitude, longitude)

    return jsonify(suggestions=[x.to_dict(simple=True) for x in candidates])
    #return jsonify(suggestions=suggestions)


def to_weighted_results(place: str, candidates: [GeoRecord], latitude: float = None, longitude: float = None) -> dict:
    if len(candidates) == 0:
        return candidates

    evaluate_distance = True if latitude or longitude else False

    weights = {
        'name': 6,
        'nearness': 4,
    }

    for candidate in candidates:
        candidate_score = get_name_score(place, candidate, weights['name'])
        if evaluate_distance:
            candidate_score += get_nearness_score(latitude, longitude, candidate, weights['nearness'])
        else:
            candidate_score += weights['nearness']


def get_name_score(place: str, candidate: GeoRecord, weight) -> float:
    name = candidate.name
    ascii_name = candidate.ascii_name
    alt_names = candidate.alternate_names

    score = 0
    highest_score = score

    if len(place) <= len(name):
        if place == name:
            return weight

        per_letter = weight / len(name)
        for i, letter in enumerate(place):
            if score >= weight:
                break

            if name[i] == letter:
                score += per_letter

        if score >= weight:
            return weight

    if score > highest_score:
        highest_score = score

    score = 0

    if len(place) <= len(ascii_name):
        if place == ascii_name:
            return weight
        per_letter = weight / len(ascii_name)
        for i, letter in enumerate(place):
            if score >= weight:
                break

            if ascii_name[i] == letter:
                score += per_letter

        if score >= weight:
            return weight

    if score > highest_score:
        highest_score = score

    score = 0

    for alt_name in alt_names:
        if len(place) <= len(alt_name):
            if place == alt_name:
                return weight
            per_letter = weight / len(alt_name)
            for i, letter in enumerate(place):
                if score >= weight:
                    break

                if alt_name[i] == letter:
                    score += per_letter

            if score >= weight:
                return weight

    return highest_score

def get_nearness_score(latitude, longitude, candidate, weight):
    pass
