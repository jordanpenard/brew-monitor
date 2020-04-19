from flask import Blueprint, url_for, request, redirect
from flask_mako import render_template

from brewmonitor.user import User, admin_required
from brewmonitor.storage import access
from brewmonitor.configuration import config

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='../../../templates/admin/',
    url_prefix='/admin',
)


@admin_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('home.index'))


@admin_bp.route('/users')
@admin_required
def admin_users():
    with config().db_connection() as db_conn:
        users = User.get_users(db_conn)
    return render_template('admin_users.html.mako', users=users)


@admin_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin')

    with config().db_connection() as db_conn:
        # TODO(tr) Do we need to encode the password as utf-8?
        User.create(db_conn, username, password, is_admin)
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/users/delete/<id>')
@admin_required
def delete_user(id):
    with config().db_connection() as db_conn:
        User.delete(db_conn, id)
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/projects')
@admin_required
def admin_projects():
    with config().db_connection() as db_conn:
        users = User.get_users(db_conn)
        projects = access.Project.get_all(db_conn)
    return render_template('admin_projects.html.mako', projects=projects, users=users)


@admin_bp.route('/sensors')
@admin_required
def admin_sensors():
    with config().db_connection() as db_conn:
        users = User.get_users(db_conn)
        sensors = access.Sensor.get_all(db_conn)
    return render_template('admin_sensors.html.mako', sensors=sensors, users=users)


@admin_bp.route('/projects/delete/<id>')
@admin_required
def delete_project(id):
    with config().db_connection() as db_conn:
        access.Project.delete(db_conn, id)
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/sensors/delete/<id>')
@admin_required
def delete_sensor(id):
    with config().db_connection() as db_conn:
        access.Sensor.delete(db_conn, id)
    return redirect(url_for('admin.admin_sensors'))


@admin_bp.route('/projects/edit/<id>', methods=['POST'])
@admin_required
def edit_project(id):
    name = request.form.get('project_name')
    owner_id = request.form.get('project_owner_id')
    with config().db_connection() as db_conn:
        access.Project.edit(db_conn, id, name, owner_id)
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/sensors/edit/<id>', methods=['POST'])
@admin_required
def edit_sensor(id):
    name = request.form.get('sensor_name')
    secret = request.form.get('sensor_secret')
    owner_id = request.form.get('sensor_owner_id')
    max_battery = request.form.get('sensor_max_battery')
    min_battery = request.form.get('sensor_min_battery')
    with config().db_connection() as db_conn:
        access.Sensor.edit(db_conn, id, name, secret, owner_id, max_battery, min_battery)
    return redirect(url_for('admin.admin_sensors'))
