from flask import Blueprint, render_template, request, jsonify
from geosuggest.geodb import db


bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


@bp.route('/', methods=['GET'])
def suggest():
    word = request.args.get('q')
    #TODO: Handle empty query
    candidates = db.find_by_name(word)
    return jsonify(suggestions=[x.as_json(simple=True) for x in candidates])
