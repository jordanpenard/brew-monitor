from flask import Blueprint, url_for, request, redirect
from flask_mako import render_template

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
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
        if id is not None:
            login_user(id, remember=remember)
            return redirect(url_for('home.index'))

        # if the above check passes, then we know the user has the right credentials
        return redirect(url_for('home.login')) # if user doesn't exist or password is wrong, reload the page

@home_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.index'))

@home_bp.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return redirect(url_for('home.index'))
    else:
        return render_template('admin_users.html.mako', users = User.get_users())

@home_bp.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        return redirect(url_for('home.index'))
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = True if request.form.get('is_admin') else False
        User.add(username, password, is_admin)
        return redirect(url_for('home.admin_users'))

@home_bp.route('/admin/users/delete/<id>')
@login_required
def delete_user(id):
    if not current_user.is_admin:
        return redirect(url_for('home.index'))
    else:
        User.delete(id)
        return redirect(url_for('home.admin_users'))
