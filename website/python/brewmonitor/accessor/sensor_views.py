from http import HTTPStatus

from flask import url_for, request, redirect
from flask_mako import render_template
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from brewmonitor.accessor._app import accessor_bp
from brewmonitor.accessor.utils import build_view_data
from brewmonitor.storage import access
from brewmonitor.utils import export_data


@accessor_bp.route('/sensor', methods=['GET'])
def all_sensors():

    return render_template(
        'accessor/sensor.html.mako',
        elem_links=access.get_sensors(),
        show_add_sensor=current_user.is_authenticated
    )


@accessor_bp.route('/sensor/<sensor_id>/', methods=['GET'])
def get_sensor(sensor_id):

    sensor = access.get_sensor_data(sensor_id)
    if sensor is None:
        abort(HTTPStatus.NOT_FOUND)

    _, linked_project = access.get_active_project_for_sensor(sensor_id)

    prev_link_projects = sensor.projects
    management_link = None
    if linked_project:
        # pop the active project so it doesn't show twice in "linked project" and "previously linked project" sections
        if linked_project.id in prev_link_projects:
            prev_link_projects.pop(linked_project.id)
        # Def is None so that it's undefined if we don't have a linked project.
        if current_user.is_authenticated:
            management_link = url_for('accessor.change_project_sensor', project_id=linked_project.id, next=request.path)

    data_links = [
        {
            'link': url_for('accessor.get_sensor_data', sensor_id=sensor.id, out_format=_format.lower()),
            'label': _format,
            'btn_class': 'btn-primary',
            'target': '_blank',
        }
        for _format in ['CSV', 'JSON']
    ]

    delete_next = url_for('accessor.get_sensor', sensor_id=sensor_id, _anchor=f'{sensor.id}_table')

    datatable, plot = build_view_data(
        'sensor',
        data_points=sensor.data_points,
        sensor_info={sensor.id: sensor},
        delete_next=delete_next,
    )
    
    return render_template(
        'accessor/view_sensor.html.mako',
        elem_obj=sensor,
        elem_name=sensor.name,
        elem_id=sensor.id,
        elem_links=prev_link_projects.values(),
        data_links=data_links,
        datatable=datatable,
        plot=plot,
        linked_elem=linked_project,
        management_link=management_link,
        allow_delete_datapoints=current_user.is_authenticated,
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
    # TODO(tr) instead of @login_required we should reject non-logged-in users with 403
    sensor = access.insert_sensor(request.form['name'], request.form['secret'], current_user)
    return redirect(url_for('accessor.get_sensor', sensor_id=sensor.id))
