from flask import Blueprint, request, jsonify, render_template
from ..errors import InvalidQuery
from ..controllers import SuggestionController

bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


# Handler for invalid queries
@bp.errorhandler(InvalidQuery)
def handle_invalid_query(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def sanitize_suggestions_parameters(req):
    # Get required and optional arguments from query
    place = req.args.get('q')
    latitude = req.args.get('latitude')
    longitude = req.args.get('longitude')
    viz = req.args.get('visualize')

    if place is None:
        raise InvalidQuery("The 'q' (partial or full name) parameter must be present.")
    else:
        place = place.strip()
    if (latitude or longitude) and (not latitude or not longitude):
        raise InvalidQuery("The 'latitude' and 'longitude' parameters must be used together.")

    # Transform latitude and longitude to floats for easier handling
    if latitude or longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            raise InvalidQuery("The 'latitude' and 'longitude' parameters must be in decimal notation")

    if latitude is not None:
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise InvalidQuery("Invalid latitude/longitude. Valid values are [-90,90] and [-180,180] respectively.")

    if viz:
        if viz.lower() in ['yes', 'true', '1']:
            viz = True
        elif viz.lower() in ['no', 'false', '0']:
            viz = False
        else:
            raise InvalidQuery("The 'viz' parameter must a value in: ['yes', 'no', 'true', 'false', '0', '1']")
    else:
        viz = False

    return place, latitude, longitude, viz


# Main route for suggestions
# Required: q
# Optional: latitude, longitude & viz
# Usage: GET /suggestions?q=<search_term>&latitude=<float>&longitude=<float>&viz=<truthy/falsy>
@bp.route('/', methods=['GET'])
def suggest():
    place, latitude, longitude, viz = sanitize_suggestions_parameters(request)

    result = SuggestionController.get_suggestions(place, latitude, longitude)

    if viz:
        return render_template('visualize.html', title='Visualization',
                               markers=result, search_term=place, latitude=latitude, longitude=longitude)
    else:
        return jsonify(suggestions=result)
