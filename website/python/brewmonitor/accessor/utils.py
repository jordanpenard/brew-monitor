from typing import List, Dict, Optional, Tuple, AnyStr

from flask import url_for

from brewmonitor.storage import access


def build_view_data(
    elem_name: str,
    data_points: List[access.DataPoints],
    delete_next: Optional[str] = None,
) -> Tuple[List, Dict]:

    datatable = []

    def _new_sensor(sensor_name: str) -> List:
        temperature_data = {
            'x': [],
            'y': [],
            'name': f'{sensor_name} temperature',
            'type': 'scatter',
            'yaxis': 'y',
        }
        angle_data = {
            'x': [],
            'y': [],
            'name': f'{sensor_name} angle',
            'type': 'scatter',
            'yaxis': 'y2',
        }
        battery_data = {
            'x': [],
            'y': [],
            'name': f'{sensor_name} battery (V)',
            'type': 'scatter',
            'yaxis': 'y3',
        }
        return [temperature_data, angle_data, battery_data]

    sensor_data = {}

    plot = {
        'data': [],
        'layout': {
            'autosize': True,
            'title': f'{elem_name} data',
            'xaxis': {
                'title': 'Date',
            },
            'yaxis': {
                'title': 'Temperature (C)',
                'overlaying': 'y3',
                'side': 'left',
            },
            'yaxis2': {
                'title': 'Angle (&deg;)',
                'overlaying': 'y3',
                'side': 'right',
            },
            'yaxis3': {
                'title': 'Battery (V)',
                'visible': False,
            },
        },
    }

    def _add(data: Dict, x: AnyStr, y: AnyStr):
        data['x'].append(x)
        data['y'].append(y)

    for entry in data_points:
        dt = entry.as_datatable()
        if delete_next:
            dt['delete_link'] = url_for('accessor.remove_datapoint', datapoint_id=entry.id, next=delete_next)
        datatable.append(dt)

        if entry.sensor_id not in sensor_data:
            # TODO(tr) Get the sensor's name
            sensor_data[entry.sensor_id] = _new_sensor(f'sensor {entry.sensor_id}')

        _add(sensor_data[entry.sensor_id][0], entry.timestamp_as_str(), entry.temperature_as_str())
        _add(sensor_data[entry.sensor_id][1], entry.timestamp_as_str(), entry.angle_as_str())
        _add(sensor_data[entry.sensor_id][2], entry.timestamp_as_str(), entry.battery_as_str())

    for s in sorted(sensor_data.keys()):
        plot['data'] += sensor_data[s]

    return datatable, plot
