from http import HTTPStatus

from flask import url_for, request, redirect
from flask_mako import render_template
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from brewmonitor.accessor._app import accessor_bp
from brewmonitor.accessor.utils import view_element
from brewmonitor.storage import access
from brewmonitor.storage.access import get_active_project_for_sensor
from brewmonitor.utils import export_data


@accessor_bp.route('/sensor', methods=['GET'])
def all_sensors():

    sensors = access.get_sensors()
    sensor_cards = [
        sensor.as_link()
        for sensor in sensors
    ]

    return render_template(
        'accessor/sensor.html.mako',
        elem_links=sensor_cards,
        show_add_sensor=current_user.is_authenticated
    )


@accessor_bp.route('/sensor/<sensor_id>/', methods=['GET'])
def get_sensor(sensor_id):

    sensor = access.get_sensor_data(sensor_id)
    if sensor is None:
        abort(HTTPStatus.NOT_FOUND)

    _, project = get_active_project_for_sensor(sensor_id)

    prev_link_projects = sensor.projects
    management_link = None
    linked_project_card = None
    if project:
        linked_project_card = project.as_link()
        # pop the active project so it doesn't show twice in "linked project" and "previously linked project" sections
        prev_link_projects.pop(project.id)
        # So that it's undefined if we don't have a linked project.
        if current_user.is_authenticated:
            management_link = url_for('accessor.change_project_sensor', project_id=project.id, next=request.path)

    prev_link_project_cards = [
        project.as_link()
        for project in prev_link_projects.values()
    ]
    data_links = [
        {
            'link': url_for('accessor.get_sensor_data', sensor_id=sensor.id, out_format=_format.lower()),
            'label': _format,
            'btn_class': 'btn-primary',
            'target': '_blank',
        }
        for _format in ['CSV', 'JSON']
    ]
    return view_element(
        'sensor',
        sensor.name,
        sensor.id,
        elem_links=prev_link_project_cards,
        data_links=data_links,
        data_points=sensor.data_points,
        linked_elem=linked_project_card,
        management_link=management_link,
        delete_next=url_for('accessor.get_sensor', sensor_id=sensor_id, _anchor=f'{sensor.id}_table'),
    )


@accessor_bp.route('/sensor/<sensor_id>/datapoints/<out_format>', methods=['GET'])
def get_sensor_data(sensor_id, out_format):

    sensor = access.get_sensor_data(sensor_id)
    if sensor is None:
        abort(HTTPStatus.NOT_FOUND)

    return export_data(f'sensor_{sensor.id}.{out_format}', str(out_format).lower(), sensor.data_points)


@accessor_bp.route('/sensor/add', methods=['POST'])
@login_required
def add_sensor():

    sensor_id = access.insert_sensor(request.form['name'], request.form['secret'], current_user.id)
    return redirect(url_for('accessor.get_sensor', sensor_id=sensor_id))
