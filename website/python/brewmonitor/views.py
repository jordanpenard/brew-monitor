from brewmonitor.configuration import config
from brewmonitor.storage.tables import User
from flask import Blueprint, current_app, redirect, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mako import render_template


home_bp = Blueprint(
    'home',
    __name__,
    template_folder='../../../templates',
)


@home_bp.route('/')
def index():
    return redirect(url_for('accessor.all_projects'))


@home_bp.route('/home')
def home():
    return render_template('home.html.mako')


@home_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html.mako')


@home_bp.route('/login', methods=['POST'])
def check_login():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember') is not None  # only has a value if ticked

    with config().db_connection() as db_conn:
        user = User.verify(db_conn, username, password)
        if user is not None:
            current_app.logger.info(f'User {user.username} is logging in.')
            login_user(user, remember=remember)
            return redirect(url_for('home.index'))

    return render_template('login.html.mako', error='Wrong credentials')


@home_bp.route('/logout')
@login_required
def logout():
    if hasattr(current_user, 'name'):
        current_app.logger.info(f'User {current_user.username} is logging out.')
    logout_user()
    return redirect(url_for('home.index'))
