from http import HTTPStatus

import attr
import pytest
from brewmonitor.storage.tables import Sensor
from flask import url_for
from test_brewmonitor.conftest import config_from_client


pages = (
    ('GET', 'admin.all_sensors', {}),
    ('GET', 'admin.delete_sensor', dict(sensor_id=42)),  # id does not matter
    ('POST', 'admin.edit_sensor', dict(sensor_id=42)),  # id does not matter
)


@pytest.mark.parametrize('method, url_str, kw', pages)
def test_public_views_redirect(public_client, url_str, kw, method):
    target = url_for(url_str, **kw)
    resp = public_client.open(target, method=method)
    assert resp.status_code == HTTPStatus.FOUND
    # redirects to home.index that redirects to accessor.all_projects
    assert resp.location == url_for('home.index', _external=True, next=target)


@pytest.mark.parametrize('method, url_str, kw', pages)
def test_non_admin_views_redirect(user_client, url_str, kw, method):
    target = url_for(url_str, **kw)
    resp = user_client.open(target, method=method)
    assert resp.status_code == HTTPStatus.FOUND
    # redirects to home.index that redirects to accessor.all_projects
    assert resp.location == url_for('home.index', _external=True, next=target)


class TestAdminViews:
    """A logged-in user that is an admin"""

    def test_all_sensors(self, admin_client):
        resp = admin_client.get(url_for('admin.all_sensors'))
        assert resp.status_code == HTTPStatus.OK

    # TODO(tr) add test when deleting an unknown sensor

    def test_delete_sensor(self, admin_user, admin_client, other_sensor):

        resp = admin_client.get(url_for('admin.delete_sensor', sensor_id=other_sensor.id))
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('admin.all_sensors', _external=True)

        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            assert Sensor.find(conn, other_sensor.id) is None, 'sensor should have been deleted'

    # TODO(tr) add test when updating an unknown sensor
    # TODO(tr) add test when updating owner_id
    # TODO(tr) add test when updating with non integer owner_id, min_battery and
    #  max_battery, see #15

    @pytest.mark.parametrize('new_sensor_data', (
        {'name': 'neo sensor 2'},
        {'secret': 'another secret'},
        {'min_battery': '1'},
        # multiple entries
        {'name': 'neo sensor 2', 'secret': 'another secret'},
        {'min_battery': '1', 'max_battery': '5'},
    ))
    def test_edit_sensor(self, admin_user, admin_client, other_sensor, new_sensor_data):
        sensor_data = {
            f'sensor_{f.name}': getattr(other_sensor, f.name)
            for f in attr.fields(Sensor)
            if f.name not in ('id', 'owner')
        }
        sensor_data['sensor_owner_id'] = str(admin_user.id)
        for k, v in new_sensor_data.items():
            sensor_data[f'sensor_{k}'] = v
            assert getattr(other_sensor, k) != v, 'test need updating'

        resp = admin_client.post(
            url_for('admin.edit_sensor', sensor_id=other_sensor.id),
            data=sensor_data,
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('admin.all_sensors', _external=True)

        bm_config = config_from_client(admin_client.application)
        with bm_config.db_connection() as conn:
            updated_new_sensor = Sensor.find(conn, other_sensor.id)
            for k, v in new_sensor_data.items():
                object_v = getattr(updated_new_sensor, k)
                if type(object_v) == float:
                    # updating the battery
                    assert object_v == float(v)
                else:
                    assert object_v == v
