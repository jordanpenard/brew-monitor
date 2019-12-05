from http import HTTPStatus

from flask import abort, url_for, request, redirect
from flask_login import login_required, current_user
from flask_mako import render_template

from brewmonitor.accessor._app import accessor_bp
from brewmonitor.accessor.utils import view_element
from brewmonitor.storage import access
from brewmonitor.utils import export_data


@accessor_bp.route('/project', methods=['GET'])
def all_projects():

    projects = access.get_projects()
    project_cards = [
        project.as_link()
        for project in projects
    ]

    return render_template(
        'accessor/project.html.mako',
        elem_links=project_cards,
        show_add_project=current_user.is_authenticated
    )


@accessor_bp.route('/project/<project_id>/', methods=['GET'])
def get_project(project_id):

    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    linked_sensor_card = None
    if project.active_sensor:
        linked_sensor_card = access.get_sensor(project.active_sensor).as_link()

    prev_link_sensors = [
        sensor.as_link()
        for sensor in project.sensors.values()
    ]
    export_data_links = [
        {
            'link': url_for('accessor.get_project_data', project_id=project.id, out_format=_format.lower()),
            'label': _format,
            'btn_class': 'btn-primary',
            'target': '_blank',
        }
        for _format in ['CSV', 'JSON']
    ]

    management_items = []
    for sensor in access.get_sensors():
        if sensor.id != project.active_sensor:
            _, active_project = access.get_active_project_for_sensor(sensor.id)

            if active_project:
                label = f'Move {sensor.name} from {active_project.name}'
            else:
                label = f'Attach {sensor.name}'
            management_items.append({
                'value': sensor.id,
                'label': label,
            })

    delete_next = url_for('accessor.get_project', project_id=project_id, _anchor=f'{project.id}_table')
    return view_element(
        'project',
        project.name,
        project.id,
        elem_links=prev_link_sensors,
        data_links=export_data_links,
        data_points=project.data_points,
        linked_elem=linked_sensor_card,
        management_link=url_for('accessor.change_project_sensor', project_id=project_id),
        management_items=management_items,
        delete_next=delete_next,
    )


@accessor_bp.route('/project/<project_id>/datapoints/<out_format>', methods=['GET'])
def get_project_data(project_id, out_format):

    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    return export_data(f'project_{project.id}.{out_format}', str(out_format).lower(), project.data_points)


@accessor_bp.route('/project/add', methods=['POST'])
@login_required
def add_project():

    project_id = access.insert_project(request.form['name'], current_user.id)
    return redirect(url_for('accessor.get_project', project_id=project_id))


@accessor_bp.route('/project/<project_id>/change_sensor', methods=['POST'])
@login_required
def change_project_sensor(project_id):

    sensor_id = request.form.get('sensor_id', 'null')  # If null we only detach the sensor
    next = request.args.get('next') or url_for('accessor.get_project', project_id=project_id)

    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    if sensor_id == 'null':
        sensor_id = None
    else:
        sensor = access.get_sensor(sensor_id)
        if sensor is None:
            abort(HTTPStatus.NOT_FOUND)

    access.update_project_sensor(project, sensor_id)
    return redirect(next)


@accessor_bp.route('/datapoint/remove/<datapoint_id>', methods=['POST'])
@login_required
def remove_datapoint(datapoint_id):

    next = request.args.get('next') or url_for('accessor.all_projects')
    access.remove_datapoint(datapoint_id)
    return redirect(next)
