import os
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from tempfile import NamedTemporaryFile
from typing import Optional

import pytest
import yaml
from brewmonitor.app import make_app
from brewmonitor.configuration import Configuration
from brewmonitor.storage.tables import Project, Sensor, User
from flask import Flask
from make_dummy_data import make_dummy_data


test_config = {
    'flask configuration': {
        'TESTING': True,
        'SERVER_NAME': 'unit-test-brewmonitor.domain',
    },
}


def config_from_client(client_obj: Flask) -> Configuration:
    return client_obj.config['brewmonitor config']


def make_clean_client(config_file: NamedTemporaryFile, db_file: NamedTemporaryFile) -> Flask:
    apply_config = deepcopy(test_config)
    apply_config['sqlite file'] = db_file.name

    yaml.dump(apply_config, config_file.file, encoding='utf-8')

    os.environ['BREWMONITOR_CONFIG'] = config_file.name

    print(f'Making app with config={config_file.name} and db={db_file.name}')
    return make_app('unit test secrets')


@pytest.fixture(scope='function')
def tmp_app() -> Flask:
    """Creates a clean db every time and destroys it at the end of the test."""
    with NamedTemporaryFile() as config_file:
        with NamedTemporaryFile() as db_file:
            yield make_clean_client(config_file, db_file)


preset_when = datetime(2021, 11, 26, 11, 34)


@pytest.fixture(scope='package')
def preset_app() -> Flask:
    """
    Creates a clean db but keeps it in between tests. Remember to clean if modified.
    Returns the app, the test client is not created and the app_context is not
    initialised.
    """
    with NamedTemporaryFile() as config_file:
        with NamedTemporaryFile() as db_file:
            app = make_clean_client(config_file, db_file)
            bm_config = config_from_client(app)
            make_dummy_data(bm_config, 'admin', when=preset_when)
            yield app


@pytest.fixture
def public_client(preset_app):
    with preset_app.test_request_context():
        with preset_app.test_client() as client:
            print('Public client')
            yield client


def find_user(db_conn, username: str) -> Optional[User]:
    cursor = db_conn.execute(
        """
        select id
        from User
        where username=?
        """,
        (username,),
    )
    # cursor.row_factory = User.row_factory
    user = cursor.fetchone()
    if user:
        return User.find(db_conn, user[0])
    return None


def find_sensor(db_conn, sensor_name: str) -> Optional[Sensor]:
    cursor = db_conn.execute(
        """
        select id
        from Sensor
        where name=?
        """,
        (sensor_name,),
    )
    # cursor.row_factory = Sensor.row_factory
    sensor = cursor.fetchone()
    if sensor is not None:
        return Sensor.find(db_conn, sensor[0])
    return None


def find_project(db_conn, project_name: str) -> Optional[Project]:
    cursor = db_conn.execute(
        """
        select id
        from Project
        where name=?
        """,
        (project_name,),
    )
    project = cursor.fetchone()
    if project is not None:
        return Project.find(db_conn, project[0])
    return None


@pytest.fixture
def normal_user(preset_app):
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        user = find_user(conn, 'titi')
        assert user, 'Should have "titi"'
        return user


@pytest.fixture
def user_client(preset_app, normal_user):
    with preset_app.test_client() as client:
        print(f'Login {normal_user}')
        resp = client.post(
            '/login',
            data={
                'username': normal_user.username,
                'password': 'pass',
            },
        )
        assert resp.status_code == HTTPStatus.FOUND
        yield client
        print(f'Logout {normal_user}')
        client.post('/logout')


@pytest.fixture
def admin_user(preset_app):
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        admin_user = find_user(conn, 'toto')
        assert admin_user, 'Should have "toto"'
        return admin_user


@pytest.fixture
def admin_client(preset_app, admin_user):
    with preset_app.test_client() as client:
        print(f'Login {admin_user}')
        resp = client.post(
            '/login',
            data={
                'username': admin_user.username,
                'password': 'admin',
            },
        )
        assert resp.status_code == HTTPStatus.FOUND
        yield client
        client.post('/logout')


@pytest.fixture
def new_user_data(preset_app):
    """Create some user data assuming it will be created and delete it afterwards

    Do NOT change the username in the test
    """
    user_data = {
        # TODO(tr) make the username random
        'username': 'new_user',
        'password': 'my_pwd',
    }
    yield user_data
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        user = find_user(conn, user_data['username'])
        if user:
            print(f'Deleting {user}')
            user.delete(conn)


@pytest.fixture
def new_sensor_data(preset_app):
    """Create some sensor data assuming it will be created in a test.
    Delete the sensor after the test if it still exists.

    Do NOT change the name in the test otherwise the deletion will fail.
    """
    sensor_data = {
        # TODO(tr) make the name random
        'name': 'new sensor',
        'secret': 'my_pwd',
    }
    yield sensor_data
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        sensor = find_sensor(conn, sensor_data['name'])
        if sensor:
            print(f'Deleting {sensor}')
            sensor.delete(conn)


@pytest.fixture
def other_sensor(preset_app, admin_user):
    """Create some sensor data assuming it will be created and delete it afterwards"""
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        # TODO(tr) make the name random
        new_sensor = Sensor.create(
            conn,
            owner=admin_user,
            name='sensor',
            secret='sensor_secret',
        )
    yield new_sensor
    with bm_config.db_connection() as conn:
        s = Sensor.find(conn, new_sensor.id)
        if s:
            print(f'Deleting {s}')
            s.delete(conn)


@pytest.fixture
def new_project_data(preset_app):
    """Create some project data assuming it will be created in a test.
    Delete the project after the test if it still exists.

    Do NOT change the name in the test otherwise the deletion will fail.
    """
    project_data = {
        # TODO(tr) make the name random
        'name': 'new project',
    }
    yield project_data
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        project = find_project(conn, project_data['name'])
        if project:
            print(f'Deleting {project}')
            project.delete(conn)


@pytest.fixture
def other_project(preset_app, admin_user):
    """Create some project data assuming it will be created and delete it afterwards"""
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        # TODO(tr) make the name random
        new_project = Project.create(
            conn,
            owner=admin_user,
            name='super beer',
        )
    yield new_project

    with bm_config.db_connection() as conn:
        p = Project.find(conn, new_project.id)
        if p:
            print(f'Deleting {p}')
            p.delete(conn)
