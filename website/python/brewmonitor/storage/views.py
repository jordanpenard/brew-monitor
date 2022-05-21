from datetime import datetime
from http import HTTPStatus

import attr
from brewmonitor.storage import access, tables
from brewmonitor.utils import json_response
from flask import Blueprint, current_app, request


storage_bp = Blueprint(
    'storage',
    __name__,
    template_folder='../../../templates/storage/',
    url_prefix='/storage',
)


@storage_bp.route('/sensor/add_data', methods=['POST'])
def add_data():

    if request.headers.get('Content-Type') != 'application/json':
        return json_response({'error': 'Content-Type header must be application/json'})

    json_args = request.get_json()
    current_app.logger.debug(f'Received json_args={json_args}')

    request_secret = json_args.pop('secret', None)
    if request_secret is None:
        return json_response({'errors': ["Missing mandatory field 'secret'"]}, HTTPStatus.BAD_REQUEST)

    if 'timestamp' not in json_args:
        json_args['timestamp'] = datetime.now()

    try:
        d = tables.Datapoint(
            project_id=None,  # populated once we got the sensor id
            **json_args,
        )
    except Exception as e:
        return json_response({'errors': [f'Failed to construct datapoint: {e}']}, HTTPStatus.BAD_REQUEST)

    sensor, project = access.get_active_project_for_sensor(d.sensor_id)
    if sensor is None:
        return json_response({'errors': [f'Did not find the sensor {d.sensor_id!r}']}, HTTPStatus.NOT_FOUND)

    if not sensor.verify_identity(request_secret):
        return json_response({'errors': ['Invalid sensor identification']}, HTTPStatus.NOT_FOUND)

    if project is not None:
        d.project_id = project.id

    access.insert_datapoints([d])

    return json_response(
        {'created': [attr.asdict(d)]},
        headers=[
            ('project_id', project.id if project else None),
        ],
    )
