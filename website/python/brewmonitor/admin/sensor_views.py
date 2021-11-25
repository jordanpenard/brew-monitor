from http import HTTPStatus

from flask import url_for, request
from flask_mako import render_template
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from brewmonitor.admin._app import admin_bp
from brewmonitor.configuration import config
from brewmonitor.storage import access
from brewmonitor.storage.tables import Sensor, User
from brewmonitor.decorators import admin_required


@admin_bp.route('/sensors')
@admin_required
def admin_sensors():
    with config().db_connection() as db_conn:
        users = User.get_all(db_conn)
        sensors = Sensor.get_all(db_conn)
    return render_template('admin_sensors.html.mako', sensors=sensors, users=users)


@admin_bp.route('/sensor/<sensor_id>/delete')
@admin_required
def delete_sensor(sensor_id):
    sensor = access.get_sensor(sensor_id)
    if sensor is None:
        abort(HTTPStatus.NOT_FOUND)

    access.remove_sensor(sensor)
    return redirect(url_for('admin.accessor.admin_sensors'))


@admin_bp.route('/sensor/<sensor_id>/edit', methods=['POST'])
@admin_required
def edit_sensor(sensor_id):
    sensor = access.get_sensor(sensor_id)
    if sensor is None:
        abort(HTTPStatus.NOT_FOUND)

    name = request.form['sensor_name']
    secret = request.form['sensor_secret']
    owner_id = int(request.form['sensor_owner_id'])
    max_battery = int(request.form['sensor_max_battery'])
    min_battery = int(request.form['sensor_min_battery'])

    owner = access.get_user(owner_id)
    if owner is None:
        abort(HTTPStatus.BAD_REQUEST)  # unknown user

    access.edit_sensor(sensor, name, secret, owner, max_battery, min_battery)
    return redirect(url_for('admin.admin_sensors'))
