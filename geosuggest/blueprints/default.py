from flask import Blueprint, render_template, request

bp = Blueprint('default', __name__)


@bp.route('/')
def index():
    return render_template('home.html')
