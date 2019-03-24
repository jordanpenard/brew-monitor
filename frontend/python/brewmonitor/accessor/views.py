from typing import List, Dict

from flask import Blueprint, abort, url_for, Response
from flask_mako import render_template

from brewmonitor.storage import access
from brewmonitor.utils import export_data

accessor_bp = Blueprint(
    'accessor',
    __name__,
    template_folder='../../../templates/accessor/',
    url_prefix='/accessor'
)


def _view_element(elem_name, elem_id, elem_links, data_links, data_points):
    # type: (str, str, List[Dict], List[Dict], List[access.DataPoints]) -> Response
    datatable = [
        {
            'when': {
                'label': access.timestamp_as_str(entry.timestamp),
                'timestamp': entry.timestamp
            },
            'gravity': str(entry.gravity),
            'temperature': str(entry.temperature),
        }
        for entry in data_points
    ]

    return render_template(
        'view_data.html.mako',
        elem_name=elem_name,
        elem_id=elem_id,
        elem_links=elem_links,
        data_links=data_links,
        datatable=datatable,
    )


#
# Routes
#


@accessor_bp.route('/', methods=['GET'])
def index():
    return render_template(
        'accessor/home.html.mako',
        projects=access.get_projects()
    )


@accessor_bp.route('/project/<project_id>/', methods=['GET'])
def get_project(project_id):

    project = access.get_project_data(project_id)
    if project is None:
        abort(404)

    elem_links = [
        {
            'link': url_for('accessor.get_sensor', sensor_id=sensor.id) if sensor.name else None,
            'label': sensor.name or '<deleted>',
            'last_active': sensor.last_active_str(),
            # We should change the btn class depending on how old is the last activity
            'btn_class': 'btn-success' if sensor.name else 'btn-secondary',
        }
        for sensor in project.sensors.values()
    ]
    data_links = [
        {
            'link': url_for('accessor.get_project_data', project_id=project.id, format=format.lower()),
            'label': format,
            'last_active': None,
            'btn_class': 'btn-primary',
            'target': '_blank',
        }
        for format in ['CSV', 'JSON']
    ]
    return _view_element(
        project.name,
        project.id,
        elem_links,
        data_links,
        project.data_points
    )


@accessor_bp.route('/project/<project_id>/datapoints/<format>', methods=['GET'])
def get_project_data(project_id, format):

    project = access.get_project_data(project_id)
    if project is None:
        abort(404)

    return export_data(f'{project.id}.{format}', str(format).lower(), project.data_points)


@accessor_bp.route('/sensor/<sensor_id>/', methods=['GET'])
def get_sensor(sensor_id):

    sensor = access.get_sensor_data(sensor_id)
    if sensor is None:
        abort(404)

    elem_links = [
        {
            'link': url_for('accessor.get_project', project_id=project.id) if project.name else None,
            'label': project.name or '<deleted>',
            'last_active': None,  # project.last_active_str()
            # We should change the btn class depending on how old is the last activity
            'btn_class': 'btn-success' if project.name else 'btn-secondary',
        }
        for project in sensor.projects.values()
    ]
    data_links = [
        {
            'link': url_for('accessor.get_sensor_data', sensor_id=sensor.id, format=format.lower()),
            'label': format,
            'last_active': None,
            'btn_class': 'btn-primary',
            'target': '_blank',
        }
        for format in ['CSV', 'JSON']
    ]
    return _view_element(
        sensor.name,
        sensor.id,
        elem_links,
        data_links,
        sensor.data_points
    )


@accessor_bp.route('/sensor/<sensor_id>/datapoints/<format>', methods=['GET'])
def get_sensor_data(sensor_id, format):

    sensor = access.get_sensor_data(sensor_id)
    if sensor is None:
        abort(404)

    return export_data(f'{sensor.id}.{format}', str(format).lower(), sensor.data_points)
