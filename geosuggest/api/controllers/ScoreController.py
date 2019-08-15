from geopy import distance
from difflib import SequenceMatcher
from geosuggest.geodb import GeoRecord


def evaluate(place: str, candidates: [GeoRecord], latitude: float = None, longitude: float = None) -> [dict]:
    # If there are no potential candidates, return immediately (implicitly returning [])
    if len(candidates) == 0:
        return candidates

    evaluate_distance = True if latitude or longitude else False

    # Name similarity is given a weight of 60% of the candidate score, proximity 40%
    weights = {
        'name': 0.70,
        'proximity': 0.30,
    }

    suggestions = []

    # Evaluate each candidate score according to name similarity and proximity
    for candidate in candidates:
        candidate_score = get_name_score(place, candidate, weights['name'])
        if evaluate_distance:
            if candidate.latitude == latitude and candidate.longitude == longitude:
                candidate_score = 1
            else:
                candidate_score += get_proximity_score(latitude, longitude, candidate, weights['proximity'])
        else:
            candidate_score += weights['proximity']

        # Combine candidate and calculated score
        suggestions.append({**candidate.to_dict(simple=True), "score": float('%.2f' % candidate_score)})

    return suggestions


def get_name_score(place: str, candidate: GeoRecord, weight) -> float:
    # Evaluate string similarity between user query and candidate's name and ascii_name
    scores = [SequenceMatcher(a=place, b=candidate.name), SequenceMatcher(a=place, b=candidate.ascii_name)]

    # Return the highest ratio of similarity, rebalanced on a scale of [0, weight]
    return max([score.ratio() for score in scores]) * weight


def get_proximity_score(latitude: float, longitude: float, candidate: GeoRecord, weight: float) -> float:
    canada_us_diameter = 6430  # approximate, in km

    # Evaluate distance between user supplied coordinates and candidate
    position = (latitude, longitude)
    candidate_position = (candidate.latitude, candidate.longitude)
    distance_between = distance.distance(position, candidate_position).kilometers
    # Translate from scale [0, canada_us_diameter] to [0, weight]
    score = weight - ((distance_between * weight) / canada_us_diameter)

    return score
