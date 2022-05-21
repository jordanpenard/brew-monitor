import dataclasses
from typing import Dict, List, Tuple

from brewmonitor.storage.tables import Datapoint, Sensor
from flask import url_for


# A dictionary that contains the Plotly trace fields.
TraceDict = Dict


@dataclasses.dataclass
class SensorTraces:
    name: str
    traces: Dict[str, TraceDict] = dataclasses.field(default_factory=dict)

    def add_trace(self, trace: str, yaxis: str):
        self.traces[trace] = {
            'x': [],
            'y': [],
            'name': f'{self.name} {trace}',
            'type': 'scatter',
            'yaxis': yaxis,
        }

    def add_point(self, trace: str, x: str, y: str):
        self.traces[trace]['x'].append(x)
        self.traces[trace]['y'].append(y)


def build_view_data(
    elem_name: str,
    data_points: List[Datapoint],
    sensor_info: Dict[int, Sensor] = None,
    delete_next: str = None,
) -> Tuple[List, Dict]:
    datatable = []
    if sensor_info is None:
        sensor_info = {}

    # Data by sensor.
    sensor_data: Dict[str, SensorTraces] = {}

    # Plotly structure, ready to give to JS library.
    plot = {
        'data': [],
        'layout': {
            'autosize': True,
            'title': f'{elem_name} data'.title(),
            'xaxis': {
                'title': 'Date',
            },
            'yaxis': {
                'title': 'Temperature (C)',
                'side': 'left',
            },
            'yaxis2': {
                'title': 'Angle (&deg;)',
                'overlaying': 'y',
                'side': 'right',
            },
        },
    }

    for entry in data_points:
        dt = entry.as_datatable()
        if delete_next:
            dt['delete_link'] = url_for('accessor.remove_datapoint', datapoint_id=entry.id, next=delete_next)
        datatable.append(dt)

        st = sensor_data.get(entry.sensor_id)
        if st is None:
            sensor = sensor_info.get(entry.sensor_id)
            if sensor is None:
                sensor_name = f'sensor {entry.sensor_id}'
            else:
                sensor_name = sensor.name
            st = SensorTraces(sensor_name)
            st.add_trace('temperature', 'y')
            st.add_trace('angle', 'y2')
            sensor_data[entry.sensor_id] = st

        when = entry.timestamp_as_str()
        st.add_point('temperature', when, entry.temperature_as_str())
        st.add_point('angle', when, entry.angle_as_str())

    for s in sorted(sensor_data.keys()):
        plot['data'] += list(sensor_data[s].traces.values())

    return datatable, plot
