from flask import Blueprint, url_for
from flask_mako import render_template

home_bp = Blueprint(
    'home',
    __name__,
    template_folder='../../../templates',
)


@home_bp.route('/')
def index():
    return render_template(
        'home.html.mako'
    )


@home_bp.route('/login')
def login():
    # TODO(tr) implement using flask-login
    # TODO(tr) Handle the next parameter so we can redirect to the appropriate page.
    return ''
