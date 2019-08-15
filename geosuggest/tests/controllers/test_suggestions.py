from geosuggest.api.controllers.SuggestionController import get_suggestions


def test_sorted_suggestions():
    place = "Toronto"
    latitude = 43.70011
    longitude = -12.4163
    suggestions = get_suggestions(place, latitude=latitude, longitude=longitude)
    print([suggestion.get('score') for suggestion in suggestions])
    assert all(suggestions[i].get('score') >= suggestions[i+1].get('score') for i in range(len(suggestions)-1))
