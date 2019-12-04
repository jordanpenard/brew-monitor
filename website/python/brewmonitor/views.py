from flask import Blueprint, url_for, request, redirect
from flask_mako import render_template

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from brewmonitor.user import User, admin_required

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

@home_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html.mako')

@home_bp.route('/login', methods=['POST'])
def check_login():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = bool(request.form.get('remember'))
        
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
@admin_required
def admin_users():
    return render_template('admin_users.html.mako', users=User.get_users())

@home_bp.route('/admin/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin')
    User.add(username, password, is_admin)
    return redirect(url_for('home.admin_users'))

@home_bp.route('/admin/users/delete/<id>')
@admin_required
def delete_user(id):
    User.delete(id)
    return redirect(url_for('home.admin_users'))
