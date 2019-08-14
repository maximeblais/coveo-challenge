from geosuggest.geodb import db
from . import ScoreController


def get_suggestions(place: str, latitude: float = None, longitude: float = None):
    # Find potential candidates and calculate their score
    candidates = db.find_by_name(place)
    suggestions = sorted(ScoreController.evaluate(place, candidates, latitude, longitude), key=lambda sugg: sugg['score'],
                         reverse=True)
    return suggestions
