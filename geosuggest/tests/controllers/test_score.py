from geosuggest.api.controllers import ScoreController
from geosuggest.geodb import db


# Verify that if we submit an empty candidate list, we get back an empty list
def test_empty_candidate_list():
    suggestions = ScoreController.evaluate('any', candidates=[])
    assert len(suggestions) == 0


# Verify that a single candidate and an exact name match gets a perfect score
def test_single_candidate_exact_name_score_is_1():
    name = 'Victoriaville'
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates)
    assert len(suggestions) == len(candidates) == 1
    assert suggestions[0].get('score') == 1


# Verify that a single candidate with a partial name match does not get a perfect score
def test_single_candiate_partial_name_score_lesser_than_1():
    name = 'Truth or Consequen'
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates)
    assert len(suggestions) == len(candidates) == 1
    assert suggestions[0].get('score') < 1


# Verify that a single candidate with a partial name match and inexact coordinates does not get a perfect score
def test_single_candidate_exact_name_inexact_coordinates_score_lesser_than_1():
    name = 'Victoriaville'
    latitude = 46.05007
    longitude = -22
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates, latitude=latitude, longitude=longitude)
    assert len(suggestions) == len(candidates) == 1
    assert suggestions[0].get('score') < 1


# Verify that a single candidate with an exact name match but exact coordinates gets a perfect score
def test_single_candidate_partial_name_exact_coordinates_score_is_1():
    name = 'Truth'
    latitude = 33.1284
    longitude = -107.25281
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates, latitude=latitude, longitude=longitude)
    assert len(suggestions) == len(candidates) == 1
    assert suggestions[0].get('score') == 1


# Verify that multiple candidates with exact name matches all get a perfect score if no coordinates are given
def test_multiple_candidates_exact_name_score_is_1():
    name = 'Toronto'
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates)
    assert len(suggestions) == len(candidates)
    for suggestion in suggestions:
        assert suggestion.get('score') == 1


# Verify that with multiple candidates with exact name matches, we get a perfect score for the candidate where
# coordinates are exact
def test_multiple_candidates_exact_name_exact_coordinates_score_is_1():
    name = 'Toronto'
    latitude = 43.70011
    longitude = -79.4163
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates, latitude=latitude, longitude=longitude)
    assert len(suggestions) == len(candidates)
    assert any(suggestion.get('score') == 1 for suggestion in suggestions)


# Verify that multiple candidates with partial name matches get a perfect score if exact coordinates are given
def test_multiple_candidates_partial_name_exact_coordinates_score_is_1():
    name = 'T'
    latitude = 43.70011
    longitude = -79.4163
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates, latitude=latitude, longitude=longitude)
    assert len(suggestions) == len(candidates)
    assert any(suggestion.get('score') == 1 for suggestion in suggestions)


# Verify that multiple candidates with partial name matches and inexact coordinates all get a less then perfect score
def test_multiple_candidates_partial_name_inexact_coordinates_score_is_lesser_than_1():
    name = 'T'
    latitude = 1
    longitude = -1
    candidates = db.find_by_name(name)
    suggestions = ScoreController.evaluate(name, candidates, latitude=latitude, longitude=longitude)
    assert len(suggestions) == len(candidates)
    assert all(suggestion.get('score') < 1 for suggestion in suggestions)
