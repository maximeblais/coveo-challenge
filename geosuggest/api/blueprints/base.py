from flask import Blueprint, render_template

bp = Blueprint('geosuggest', __name__)


@bp.route('/')
def index():
    return render_template('home.html', title='Home')


@bp.route('/visualize')
def visualize():
    return render_template('visualize.html', title='Visualization')
