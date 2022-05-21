from datetime import datetime
from typing import List, Optional

import pytest
from brewmonitor.accessor.utils import build_view_data
from brewmonitor.storage.tables import Datapoint, Sensor
from flask import url_for


class TestBuildViewData:
    @classmethod
    @pytest.fixture
    def s1_datapoints(cls) -> List[Datapoint]:
        return [
            Datapoint(1, 1, datetime(2021, 11, 30, 9, 40), 10, 22.0, 9.6),
            Datapoint(1, 1, datetime(2021, 11, 30, 9, 45), 8, 21.0, 9.5),
            Datapoint(1, 1, datetime(2021, 11, 30, 9, 50), 6, 20.0, 9.4),
        ]

    @classmethod
    @pytest.fixture
    def s2_datapoints(cls) -> List[Datapoint]:
        return [
            Datapoint(2, 1, datetime(2021, 11, 30, 9, 55), 7, 20.2, 3.4),
            Datapoint(2, 1, datetime(2021, 11, 30, 10, 0), 9, 21.1, 3.3),
        ]

    @classmethod
    def check_s1_plot(cls, plot_data):
        # Check the layout has a title,
        # that 'y' is temperature
        # that 'y2' is angle
        # that 'y3' does not exist (it was battery)
        assert plot_data['layout']['title'] == 'My Project Data'
        assert 'xaxis' in plot_data['layout']
        assert plot_data['layout']['yaxis']['title'].startswith('Temperature')
        assert plot_data['layout']['yaxis2']['title'].startswith('Angle')
        assert 'yaxis3' not in plot_data['layout']

        # Check the data is was we would expect
        assert len(plot_data['data']) == 2, 'Should have one trace per axis'

        time_axis = list(map(Datapoint.format_timestamp, (
            datetime(2021, 11, 30, 9, 40),
            datetime(2021, 11, 30, 9, 45),
            datetime(2021, 11, 30, 9, 50),
        )))

        # check temperature trace
        assert plot_data['data'][0]['yaxis'] == 'y', 'first trace should be temperature'
        assert plot_data['data'][0]['name'] == 'sensor 1 temperature'  # sensor name was not given
        assert plot_data['data'][0]['y'] == list(map(Datapoint.format_temperature, (
            22.0, 21.0, 20.0,
        )))
        assert plot_data['data'][0]['x'] == time_axis

        # check angle trace
        assert plot_data['data'][1]['yaxis'] == 'y2', 'second trace should be angle'
        assert plot_data['data'][1]['name'] == 'sensor 1 angle'  # sensor name was not given
        assert plot_data['data'][1]['y'] == list(map(Datapoint.format_angle, (
            10.0, 8.0, 6.0,
        )))
        assert plot_data['data'][1]['x'] == time_axis

    @classmethod
    def check_s1_datatable(cls, datatable_data, delete_next: Optional[str]):
        # This is mostly testing that the fields exists, Datatpoint.as_datatable is
        # responsible for actually formatting the entry
        assert len(datatable_data) == 3

        for d in datatable_data:
            if delete_next is not None:
                assert 'delete_link' in d
            else:
                assert 'delete_link' not in d

    def test_project_graph_view(self, s1_datapoints):
        _, plot_data = build_view_data('my project', s1_datapoints, sensor_info=None, delete_next=None)
        self.check_s1_plot(plot_data)

    @pytest.mark.parametrize('delete_next', (
        None,
        # 'accessor.all_projects',  # TODO(tr) make it work
    ))
    def test_project_datatable_view(self, tmp_app, s1_datapoints, delete_next):
        with tmp_app.app_context():
            # even with the app context it rejects the creation of the url
            # with next=<next_url> even thought it works on the real server...
            if delete_next:
                next_url = url_for(delete_next)
            else:
                next_url = None
            dt_data, _ = build_view_data('my project', s1_datapoints, sensor_info=None, delete_next=next_url)
            self.check_s1_datatable(dt_data, delete_next)

    def test_sensor_graph_view(self, s1_datapoints):
        _, plot_data = build_view_data('my project', s1_datapoints, sensor_info=None, delete_next=None)
        self.check_s1_plot(plot_data)

    @pytest.mark.parametrize('delete_next', (
        None,
        # 'accessor.all_sensors',  # TODO(tr) make it work
    ))
    def test_sensor_datatable_view(self, tmp_app, s1_datapoints, delete_next):
        with tmp_app.app_context():
            # even with the app context it rejects the creation of the url
            # with next=<next_url> even thought it works on the real server...
            if delete_next:
                next_url = url_for(delete_next)
            else:
                next_url = None
            dt_data, _ = build_view_data('my project', s1_datapoints, sensor_info=None, delete_next=next_url)
            self.check_s1_datatable(dt_data, delete_next)

    def test_provide_sensor_data(self, s2_datapoints):
        _, plot_data = build_view_data(
            'my project',
            s2_datapoints,
            # real usage reads that from the db
            sensor_info={
                1: Sensor(1, 'green name', 'secret', 'toto'),  # should not be used
                2: Sensor(2, 'brown sensor', 'secret', 'toto'),
            },
            delete_next=None,
        )

        assert plot_data['data'][0]['name'] == 'brown sensor temperature'
        assert plot_data['data'][1]['name'] == 'brown sensor angle'

    def test_provide_sensor_data_but_not_found(self, s2_datapoints):
        # to check that providing sensor info without the correct sensor still works
        _, plot_data = build_view_data(
            'my project',
            s2_datapoints,
            sensor_info={
                1: Sensor(1, 'green sensor', 'secret', 'toto'),  # should not be used
                # remove so that it has to use default name
                # 2: Sensor(2, 'brown sensor', 'secret', 'toto'),
            },
            delete_next=None,
        )

        assert plot_data['data'][0]['name'] == 'sensor 2 temperature', 'should use id as name'
        assert plot_data['data'][1]['name'] == 'sensor 2 angle', 'should use id as name'

    def test_multiple_sensors_make_multiple_traces(self, s1_datapoints, s2_datapoints):
        _, plot_data = build_view_data(
            'my project',
            s1_datapoints + s2_datapoints,
            sensor_info={
                1: Sensor(1, 'green sensor', 'secret', 'toto'),
                2: Sensor(2, 'brown sensor', 'secret', 'toto'),
            },
            delete_next=None,
        )

        assert len(plot_data['data']) == 4, 'Should have 2 trace per sensor'
        assert plot_data['data'][0]['name'] == 'green sensor temperature'
        assert plot_data['data'][1]['name'] == 'green sensor angle'
        assert plot_data['data'][2]['name'] == 'brown sensor temperature'
        assert plot_data['data'][3]['name'] == 'brown sensor angle'
