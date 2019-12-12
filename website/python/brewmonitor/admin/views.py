from flask import Blueprint, url_for, request, redirect
from flask_mako import render_template
from brewmonitor.user import User, admin_required

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='../../../templates/admin/',
    url_prefix='/admin'
)

@admin_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('home.index'))

@admin_bp.route('/users')
@admin_required
def admin_users():
    return render_template('admin_users.html.mako', users=User.get_users())

@admin_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin')
    User.add(username, password, is_admin)
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/users/delete/<id>')
@admin_required
def delete_user(id):
    User.delete(id)
    return redirect(url_for('admin.admin_users'))
