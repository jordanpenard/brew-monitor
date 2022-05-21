import abc
import os
from copy import deepcopy
from tempfile import NamedTemporaryFile
from typing import Optional

import yaml
from brewmonitor.app import make_app
from brewmonitor.configuration import Configuration
from brewmonitor.storage.tables import Project, Sensor, User
from flask import Flask
from test_brewmonitor.constants import test_config


class MultiClientBase(metaclass=abc.ABCMeta):
    """Use this when the same test is needed for public, user or admin"""

    @abc.abstractmethod
    def _check_view(self, client):
        # TODO(tr) I need to find a better way to do that that can take other fixtures etc
        ...

    def test_public_view(self, public_client):
        self._check_view(public_client)

    def test_user_view(self, user_client):
        self._check_view(user_client)

    def test_admin_view(self, admin_client):
        self._check_view(admin_client)


def config_from_client(client_obj: Flask) -> Configuration:
    return client_obj.config['brewmonitor config']


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


def make_clean_client(config_file: NamedTemporaryFile, db_file: NamedTemporaryFile) -> Flask:
    apply_config = deepcopy(test_config)
    apply_config['sqlite file'] = db_file.name

    yaml.dump(apply_config, config_file.file, encoding='utf-8')

    os.environ['BREWMONITOR_CONFIG'] = config_file.name

    print(f'Making app with config={config_file.name} and db={db_file.name}')
    return make_app('unit test secrets')
