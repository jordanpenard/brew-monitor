from flask import Blueprint, url_for, request, redirect
from flask_mako import render_template

from brewmonitor.user import User, admin_required
from brewmonitor.storage.access import Project, Sensor
from brewmonitor.storage import access

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

@admin_bp.route('/projects')
@admin_required
def admin_projects():
    return render_template('admin_projects.html.mako', projects=access.get_projects())

@admin_bp.route('/sensors')
@admin_required
def admin_sensors():
    return render_template('admin_sensors.html.mako', sensors=access.get_sensors())

@admin_bp.route('/projects/delete/<id>')
@admin_required
def delete_project(id):
    Project.delete(id)
    return redirect(url_for('admin.admin_projects'))

@admin_bp.route('/sensors/delete/<id>')
@admin_required
def delete_sensor(id):
    Sensor.delete(id)
    return redirect(url_for('admin.admin_sensors'))
