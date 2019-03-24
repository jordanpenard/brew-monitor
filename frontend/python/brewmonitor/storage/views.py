from datetime import datetime

import attr
from flask import Blueprint, request

from brewmonitor.storage.access import (
    get_active_project_for_sensor,
    DataPoints,
    insert_datapoints,
)
from brewmonitor.utils import json_response

storage_bp = Blueprint(
    'storage',
    __name__,
    template_folder='../../../templates/storage/',
    url_prefix='/storage'
)


@storage_bp.route('/sensor/add_data', methods=['POST'])
def add_data():

    if request.headers.get('Content-Type') != 'application/json':
        return json_response({"error": "Content-Type header must be application/json"})

    json_args = request.get_json()
    print (f'Received json_args={json_args}')
    if 'timestamp' not in json_args:
        json_args['timestamp'] = datetime.now().timestamp()

    try:
        d = DataPoints(
            project_id=None,  # populated once we got the sensor id
            **json_args
        )
    except Exception as e:
        return json_response({"errors": [f"Failed to construct datapoint: {e}"]}, 400)

    sensor, project = get_active_project_for_sensor(d.sensor_id)
    if sensor is None:
        return json_response({"errors": [f"Did not find the sensor {d.sensor_id!r}"]}, 404)

    if project is not None:
        d.project_id = project.id

    insert_datapoints(d)

    return json_response(
        {"created": [attr.asdict(d)]},
        headers=[
            ('project_id', project.id),
        ],
    )
