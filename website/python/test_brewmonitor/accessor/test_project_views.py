from http import HTTPStatus

import pytest
from flask import url_for

from brewmonitor.storage.tables import Project, Sensor
from test_brewmonitor.conftest import config_from_client, find_project, find_sensor
from test_brewmonitor.utils import MultiClientBase


class TestAllProjects(MultiClientBase):
    def _check_view(self, client):
        resp = client.get(url_for('accessor.all_projects'))
        assert resp.status_code == HTTPStatus.OK

    # TODO(tr) check that logged-in users can see the "add project" part


class TestGetProjectOk(MultiClientBase):
    def _check_view(self, client):
        bm_config = config_from_client(client.application)
        with bm_config.db_connection() as conn:
            project_a = find_project(conn, 'Sad project')  # sensor not attached
            project_b = find_project(conn, 'Brown Ale #12')  # sensor attached
            assert project_a.active_sensor is None, 'should not have an attached sensor'
            assert project_b.active_sensor is not None, 'should have an attached sensor'

        resp = client.get(url_for('accessor.get_project', project_id=project_a.id))
        assert resp.status_code == HTTPStatus.OK

        resp = client.get(url_for('accessor.get_project', project_id=project_b.id))
        assert resp.status_code == HTTPStatus.OK


class TestGetProjectNotFound(MultiClientBase):
    def _check_view(self, client):
        resp = client.get(url_for('accessor.get_project', project_id=42))
        assert resp.status_code == HTTPStatus.NOT_FOUND


class TestGetProjectDataOk(MultiClientBase):
    supported_formats = ('csv', 'json')

    def _check_view(self, client):
        bm_config = config_from_client(client.application)
        with bm_config.db_connection() as conn:
            project_a = find_project(conn, 'Brown Ale #12')  # sensor attached + data

        for fmt in self.supported_formats:
            resp = client.get(url_for('accessor.get_project_data', project_id=project_a.id, out_format=fmt))
            assert resp.status_code == HTTPStatus.OK


class TestGetProjectDataNotFound(MultiClientBase):
    def _check_view(self, client):
        resp = client.get(url_for('accessor.get_project_data', project_id=42, out_format='csv'))
        assert resp.status_code == HTTPStatus.NOT_FOUND


class TestGetProjectDataBadRequest(MultiClientBase):
    def _check_view(self, client):
        bm_config = config_from_client(client.application)
        with bm_config.db_connection() as conn:
            project_a = find_project(conn, 'Brown Ale #12')

        resp = client.get(url_for('accessor.get_project_data', project_id=project_a.id, out_format='xls'))
        assert resp.status_code == HTTPStatus.BAD_REQUEST


class TestAddProject:

    def test_public_redirect(self, public_client):
        target = url_for('accessor.add_project')
        resp = public_client.post(target, data={})
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('home.index', _external=True, next=target)

    def test_user_add_project(self, user_client, normal_user, new_project_data):
        target = url_for('accessor.add_project')
        resp = user_client.post(target, data=new_project_data)
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location != url_for('home.index', _external=True, next=target)

        bm_config = config_from_client(user_client.application)
        with bm_config.db_connection() as conn:
            project = find_project(conn, new_project_data['name'])
        assert project is not None, 'project should have been created'
        assert project.owner == normal_user.username

        assert resp.location == url_for('accessor.get_project', _external=True, project_id=project.id)


class TestChangeProjectSensor:
    # One of the limitation of that view is that any logged-in user can change the sensor
    # We should probably limit this to the owner or an admin.
    # Meanwhile we test for it in every view that modifies the project.
    #
    # We do not have to test that "Project.attach_sensor" first detaches the sensor if it's
    # already attached because we should be testing that in the storage tests.
    #
    # We also check the redirect works (to_sensor) because this endpoint is contacted by the sensor page as well.

    def test_public_redirect(self, public_client, other_project):
        target = url_for('accessor.change_project_sensor', project_id=other_project.id)
        resp = public_client.post(target, data={})
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location == url_for('home.index', _external=True, next=target)

    @pytest.mark.parametrize('to_sensor', (True, False))
    def test_user_attach_sensor(self, user_client, normal_user, other_project, other_sensor, to_sensor):
        # No sensor attached yet, attach one
        assert other_project.owner != normal_user.username
        assert other_project.active_sensor is None, 'should not have an attached sensor yet'

        if to_sensor:
            redirect = url_for('accessor.get_sensor', _external=True, sensor_id=other_sensor.id)
            target = url_for('accessor.change_project_sensor', project_id=other_project.id, next=redirect)
        else:
            target = url_for('accessor.change_project_sensor', project_id=other_project.id)
            redirect = url_for('accessor.get_project', _external=True, project_id=other_project.id)

        resp = user_client.post(target, data={'sensor_id': str(other_sensor.id)})
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location != url_for('home.index', _external=True, next=target)

        bm_config = config_from_client(user_client.application)
        with bm_config.db_connection() as conn:
            project = Project.find(conn, other_project.id)
            assert project.active_sensor == other_sensor.id

        assert resp.location == redirect

    @pytest.mark.parametrize('to_sensor', (True, False))
    def test_user_change_sensor(self, user_client, normal_user, other_project, other_sensor, new_sensor_data, to_sensor):
        # a sensor is attached but we change it
        assert other_project.owner != normal_user.username
        bm_config = config_from_client(user_client.application)
        with bm_config.db_connection() as conn:
            existing = Sensor.create(
                conn,
                owner=normal_user,
                **new_sensor_data,
            )
            other_project.attach_sensor(conn, existing.id)
        assert other_project.active_sensor != other_sensor.id

        if to_sensor:
            redirect = url_for('accessor.get_sensor', _external=True, sensor_id=other_sensor.id)
            target = url_for('accessor.change_project_sensor', project_id=other_project.id, next=redirect)
        else:
            target = url_for('accessor.change_project_sensor', project_id=other_project.id)
            redirect = url_for('accessor.get_project', _external=True, project_id=other_project.id)

        resp = user_client.post(target, data={'sensor_id': str(other_sensor.id)})
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location != url_for('home.index', _external=True, next=target)

        with bm_config.db_connection() as conn:
            project = Project.find(conn, other_project.id)
            assert project.active_sensor == other_sensor.id

        assert resp.location == redirect

    @pytest.mark.parametrize('send_null', (True, False))
    @pytest.mark.parametrize('to_sensor', (True, False))
    def test_user_detach_sensor(self, user_client, normal_user, other_project, other_sensor, send_null, to_sensor):
        # a sensor is attached but we detach it
        assert other_project.owner != normal_user.username
        bm_config = config_from_client(user_client.application)
        with bm_config.db_connection() as conn:
            other_project.attach_sensor(conn, other_sensor.id)
        assert other_project.active_sensor == other_sensor.id

        if to_sensor:
            redirect = url_for('accessor.get_sensor', _external=True, sensor_id=other_sensor.id)
            target = url_for('accessor.change_project_sensor', project_id=other_project.id, next=redirect)
        else:
            target = url_for('accessor.change_project_sensor', project_id=other_project.id)
            redirect = url_for('accessor.get_project', _external=True, project_id=other_project.id)

        data = {}
        if send_null:
            data['sensor_id'] = 'null'
        resp = user_client.post(target, data=data)
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.location != url_for('home.index', _external=True, next=target)

        with bm_config.db_connection() as conn:
            project = Project.find(conn, other_project.id)
            assert project.active_sensor is None

        assert resp.location == redirect

    def test_project_not_found(self, user_client):
        target = url_for('accessor.change_project_sensor', project_id=42)
        resp = user_client.post(target, data={})
        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_sensor_not_found(self, user_client, other_project):
        target = url_for('accessor.change_project_sensor', project_id=other_project.id)
        resp = user_client.post(target, data={'sensor_id': '42'})
        assert resp.status_code == HTTPStatus.NOT_FOUND
