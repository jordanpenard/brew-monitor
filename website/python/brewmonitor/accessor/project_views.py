from http import HTTPStatus

from brewmonitor.accessor._app import accessor_bp
from brewmonitor.accessor.utils import build_view_data
from brewmonitor.storage import access
from brewmonitor.utils import export_data
from flask import abort, redirect, request, url_for
from flask_login import current_user, login_required
from flask_mako import render_template


@accessor_bp.route('/project', methods=['GET'])
def all_projects():

    return render_template(
        'accessor/project.html.mako',
        elem_links=access.get_projects(),
        show_add_project=current_user.is_authenticated,
    )


@accessor_bp.route('/project/<project_id>/', methods=['GET'])
def get_project(project_id):

    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    prev_link_sensors = []
    linked_sensor = None
    if project.active_sensor is not None:
        linked_sensor = access.get_sensor(project.active_sensor)
        for s in project.sensors.values():
            if s.id != project.active_sensor:
                prev_link_sensors.append(s)
        # ignore the active sensor so it doesn't show twice in "linked sensor"
        # and "previously linked sensor" sections

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

    management_link = None
    if current_user.is_authenticated:
        management_link = url_for('accessor.change_project_sensor', project_id=project_id)

    delete_next = url_for('accessor.get_project', project_id=project_id, _anchor=f'{project.id}_table')

    datatable, plot = build_view_data(
        'project',
        data_points=project.data_points,
        sensor_info=project.sensors,
        delete_next=delete_next,
    )

    return render_template(
        'accessor/view_project.html.mako',
        elem_obj=project,
        elem_name=project.name,
        elem_id=project.id,
        elem_links=prev_link_sensors,
        data_links=export_data_links,
        datatable=datatable,
        plot=plot,
        linked_elem=linked_sensor,
        management_link=management_link,
        management_items=management_items or None,
        allow_delete_datapoints=current_user.is_authenticated,
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

    project = access.insert_project(request.form['name'], current_user)
    return redirect(url_for('accessor.get_project', project_id=project.id))


@accessor_bp.route('/project/<project_id>/change_sensor', methods=['POST'])
@login_required
def change_project_sensor(project_id):

    sensor_id = request.form.get('sensor_id', 'null')  # If null we only detach the sensor
    next_ = request.args.get('next') or url_for('accessor.get_project', project_id=project_id)

    project = access.get_project_data(project_id)
    if project is None:
        abort(HTTPStatus.NOT_FOUND)

    if sensor_id == 'null':
        sensor_id = None
    else:
        sensor = access.get_sensor(int(sensor_id))
        if sensor is None:
            abort(HTTPStatus.NOT_FOUND)

    access.update_project_sensor(project, sensor_id)
    return redirect(next_)


@accessor_bp.route('/datapoint/<datapoint_id>/delete', methods=['POST'])
@login_required
def remove_datapoint(datapoint_id):
    next_ = request.args.get('next') or url_for('accessor.all_projects')

    datapoint = access.get_datapoint(datapoint_id)
    if datapoint is None:
        abort(HTTPStatus.NOT_FOUND)

    # TODO(tr) check if the current_user is an admin or the owner of that project?

    access.remove_datapoint(datapoint)
    return redirect(next_)
