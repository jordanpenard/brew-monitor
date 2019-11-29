from flask import Blueprint, url_for, request, redirect
from flask_mako import render_template

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from brewmonitor.user import User

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

@home_bp.route('/login', methods=['GET', 'POST'])
def login():
        
    if request.method == 'GET':
        return render_template('login.html.mako')

    else:
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        id = User.verify(username, password)
        if id != 0:
            login_user(User(id), remember=remember)
            return redirect(url_for('home.index'))

        # if the above check passes, then we know the user has the right credentials
        return redirect(url_for('home.login')) # if user doesn't exist or password is wrong, reload the page

@home_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.index'))
