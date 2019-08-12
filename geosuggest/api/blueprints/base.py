from flask import Blueprint, render_template, jsonify
from ..errors import InvalidQuery

bp = Blueprint('default', __name__)


@bp.route('/')
def index():
    return render_template('home.html')
