import os
from copy import deepcopy
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Optional

import pytest
import yaml
from flask import Flask

from brewmonitor.app import make_app
from brewmonitor.configuration import Configuration
from brewmonitor.storage.tables import User, Sensor, Project
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
    Returns the app, the test client is not created and the app_context is not initialised.
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
        '''
            select id, username, is_admin
            from User
            where username=?
        ''',
        (username,),
    )
    cursor.row_factory = User.row_factory
    return cursor.fetchone()


def find_sensor(db_conn, sensor_name: str) -> Optional[Sensor]:
    cursor = db_conn.execute(
        '''
            select id, name, secret, owner
            from Sensor
            where name=?
        ''',
        (sensor_name,),
    )
    cursor.row_factory = Sensor.row_factory
    return cursor.fetchone()


def find_project(db_conn, project_name: str) -> Optional[Project]:
    cursor = db_conn.execute(
        '''
            select id, name, owner
            from Project
            where name=?
        ''',
        (project_name,),
    )
    cursor.row_factory = Project.row_factory
    return cursor.fetchone()


@pytest.fixture
def user_client(preset_app):
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        normal_user = find_user(conn, 'titi')
        assert normal_user, 'Should have "titi"'

    with preset_app.test_client() as client:
        print(f'Login {normal_user}')
        client.post(
            '/login',
            data={
                'username': normal_user.username,
                'password': 'admin',
            },
        )
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
        client.post(
            '/login',
            data={
                'username': admin_user.username,
                'password': 'admin',
            },
        )
        yield client
        client.post('/logout')


@pytest.fixture
def other_user_data(preset_app):
    """Create some user data assuming it will be created and delete it afterwards"""
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
def other_sensor_data(preset_app):
    """Create some sensor data assuming it will be created and delete it afterwards"""
    sensor_data = {
        # TODO(tr) make the name random
        'name': 'sensor',
        'secret': 'sensor_secret',
        # owner has to be attached
    }
    yield sensor_data
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        s = find_sensor(conn, sensor_data['name'])
        if s:
            print(f'Deleting {s}')
            s.delete(conn)


@pytest.fixture
def other_project_data(preset_app):
    """Create some project data assuming it will be created and delete it afterwards"""
    project_data = {
        # TODO(tr) make the name random
        'name': 'super beer',
        # owner has to be attached
    }
    yield project_data
    bm_config = config_from_client(preset_app)
    with bm_config.db_connection() as conn:
        p = find_project(conn, project_data['name'])
        if p:
            print(f'Deleting {p}')
            p.delete(conn)
