from http import HTTPStatus

from flask import url_for

from test_brewmonitor.conftest import config_from_client, find_sensor, public_client, admin_client, user_client
from test_brewmonitor.utils import MultiClientBase


class TestAllSensors(MultiClientBase):
    def _check_view(self, client):
        resp = client.get(url_for('accessor.all_sensors'))
        assert resp.status_code == HTTPStatus.OK

    # TODO(tr) add test to check that authenticated users can see "add sensor"


class TestGetSensorOk(MultiClientBase):
    def _check_view(self, client):
        bm_config = config_from_client(client.application)
        with bm_config.db_connection() as conn:
            not_linked_sensor = find_sensor(conn, 'sad sensor')
            linked_sensor = find_sensor(conn, 'brown sensor')
            assert not_linked_sensor.linked_project is None, 'should not use a linked sensor'
            assert linked_sensor.linked_project is not None, 'should use a linked sensor'

        resp = client.get(url_for('accessor.get_sensor', sensor_id=not_linked_sensor.id))
        assert resp.status_code == HTTPStatus.OK

        resp = client.get(url_for('accessor.get_sensor', sensor_id=linked_sensor.id))
        assert resp.status_code == HTTPStatus.OK


class TestGetSensorNotFound(MultiClientBase):
    def _check_view(self, client):
        resp = client.get(url_for('accessor.get_sensor', sensor_id=42))
        assert resp.status_code == HTTPStatus.NOT_FOUND


class TestGetSensorDataOk(MultiClientBase):
    supported_formats = ('csv', 'json')

    def _check_view(self, client):
        bm_config = config_from_client(client.application)
        with bm_config.db_connection() as conn:
            linked_sensor = find_sensor(conn, 'brown sensor')

        for fmt in self.supported_formats:
            resp = client.get(url_for('accessor.get_sensor_data', sensor_id=linked_sensor.id, out_format=fmt))
            assert resp.status_code == HTTPStatus.OK


class TestGetSensorDataNotFound(MultiClientBase):
    def _check_view(self, client):
        resp = client.get(url_for('accessor.get_sensor_data', sensor_id=42, out_format='csv'))
        assert resp.status_code == HTTPStatus.NOT_FOUND


class TestGetSensorDataBadRequest(MultiClientBase):
    def _check_view(self, client):
        bm_config = config_from_client(client.application)
        with bm_config.db_connection() as conn:
            linked_sensor = find_sensor(conn, 'brown sensor')

        resp = client.get(url_for('accessor.get_sensor_data', sensor_id=linked_sensor.id, out_format='xls'))
        assert resp.status_code == HTTPStatus.BAD_REQUEST


class TestAddSensor:

    def test_public_redirect(self, public_client):
        target = url_for('accessor.add_sensor')
        resp = public_client.post(target, data={})
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('home.index', _external=True, next=target)

    def test_user_add_sensor(self, user_client, normal_user, new_sensor_data):
        target = url_for('accessor.add_sensor')
        resp = user_client.post(target, data=new_sensor_data)
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location != url_for('home.index', _external=True, next=target)

        bm_config = config_from_client(user_client.application)
        with bm_config.db_connection() as conn:
            sensor = find_sensor(conn, new_sensor_data['name'])
        assert sensor is not None, 'sensor should have been created'
        assert sensor.owner == normal_user.username

        assert resp.location == url_for('accessor.get_sensor', sensor_id=sensor.id, _external=True)
