import dataclasses
from typing import List, Dict, Optional, Tuple

from flask import url_for

from brewmonitor.storage import access

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
            'name': f"{self.name} {trace}",
            'type': 'scatter',
            'yaxis': yaxis,
        }

    def add_point(self, trace: str, x: str, y: str):
        self.traces[trace]['x'].append(x)
        self.traces[trace]['y'].append(y)


def build_view_data(
    elem_name: str,
    data_points: List[access.Datapoint],
    sensor_info: Optional[Dict[int, access.Sensor]],
    delete_next: Optional[str] = None,
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
            'title': f'{elem_name.title()} data',
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
            st = SensorTraces(sensor.name if sensor is not None else f"sensor {entry.sensor_id}")
            st.add_trace('temperature', 'y')
            st.add_trace('angle', 'y2')
            sensor_data[entry.sensor_id] = st

        when = entry.timestamp_as_str()
        st.add_point('temperature', when, entry.temperature_as_str())
        st.add_point('angle', when, entry.angle_as_str())

    for s in sorted(sensor_data.keys()):
        plot['data'] += list(sensor_data[s].traces.values())

    return datatable, plot
