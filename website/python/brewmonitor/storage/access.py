from datetime import datetime, timedelta
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple, AnyStr

import attr
from flask import url_for

from brewmonitor.utils import config
from enum import Enum

if TYPE_CHECKING:
    from brewmonitor.configuration import SQLConnection

class SensorState(Enum):
    ACTIVE = '<span style="vertical-align: middle;" class="badge badge-primary">Active</span>'       # blue
    LIVE = '<span style="vertical-align: middle;" class="badge badge-success">Live</span>'           # green
    INACTIVE = '<span style="vertical-align: middle;" class="badge badge-secondary">Inactive</span>' # gray

@attr.s
class Sensor:
    id = attr.ib(type=int)
    name = attr.ib(type=str)
    secret = attr.ib(type=str)
    owner = attr.ib(type=str)
    last_active = attr.ib(type=datetime, default=None)  # in SQL we would get that from the datapoints

    def last_active_str(self):
        # type: () -> str
        if self.last_active is not None:
            return self.last_active.isoformat()
        return 'inactive'

    def get_state(self):
        if self.last_active is not None:
            if datetime.now() - self.last_active > timedelta(days=1):
                return SensorState.ACTIVE
            else:
                return SensorState.LIVE
        else:
            return SensorState.INACTIVE

    @classmethod
    def row_factory(cls, _cursor, _row):
        d = {}
        for idx, col in enumerate(_cursor.description):
            d[col[0]] = _row[idx]
        return cls(
            d['id'],
            d['name'],
            d['secret'],
            d['owner'],
            datetime.fromisoformat(d['last_active']) if d['last_active'] else None,
        )

    @classmethod
    def get_all(cls, db_conn):
        # type: (SQLConnection) -> List[Sensor]
        # TODO(tr) Get last battery as well
        cursor = db_conn.execute(
            '''
            select id, name, secret, (select timestamp from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1) as last_active, (select username from User where id = Sensor.owner limit 1) as owner
            from Sensor;
            '''
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn, sensor_id):
        # type: (SQLConnection, int) -> Optional[Sensor]
        sens_cursor = db_conn.execute(
            '''
            select id, name, secret, (select timestamp from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1) as last_active, (select username from User where id = Sensor.owner limit 1) as owner
            from Sensor where id = ?; 
            ''',
            (sensor_id,)
        )
        sens_cursor.row_factory = cls.row_factory
        return sens_cursor.fetchone()

    def as_link(self):
        return {
            'link': url_for('accessor.get_sensor', sensor_id=self.id),
            'owner': self.owner,
            'label': self.name or '<deleted>',
            'last_active': self.last_active_str() ,
            'sensor_state': self.get_state(),
        }

    @classmethod
    def create_new(cls, db_conn, name, secret, owner):
        # type: (SQLConnection, AnyStr, Int) -> int
        cursor = db_conn.cursor()
        cursor.execute(
            '''
            insert into Sensor (name, secret, owner) values (?, ?, ?);
            ''',
            (name,secret,owner)
        )
        # lastrowid is the last successful insert on that cursor
        return cursor.lastrowid

    def verify_identity(self, request_secret):
        # type: (str) -> boot
        # Return true if the secret provided by the request matches the sensor's secret from the db
        return self.secret == request_secret

@attr.s
class Project:
    id = attr.ib(type=int)
    name = attr.ib(type=str)
    owner = attr.ib(type=str)
    active_sensor = attr.ib(default=None)  # Assuming 1 sensor per project but could change the sensor.

    @classmethod
    def row_factory(cls, _cursor, _row):
        d = {}
        for idx, col in enumerate(_cursor.description):
            d[col[0]] = _row[idx]
        return cls(
            d['id'],
            d['name'],
            d['owner'],
            d['active_sensor']
        )

    @classmethod
    def get_all(cls, db_conn):
        # type: (SQLConnection) -> List[Project]
        cursor = db_conn.execute(
            '''
            select id, name, active_sensor, (select username from User where id = Project.owner limit 1) as owner
            from Project;
            '''
        )
        # TODO(tr) Add order by last activity
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn, project_id):
        # type: (SQLConnection, int) -> Project
        cursor = db_conn.execute(
            '''
            select id, name, active_sensor, (select username from User where id = Project.owner limit 1) as owner
            from Project
            where id = ?;
            ''',
            (project_id,)
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchone()

    @classmethod
    def by_active_sensor(cls, db_conn, sensor_id):
        # type: (SQLConnection, int) -> Optional[Project]
        proj_cursor = db_conn.execute(
            '''
            select id, name, active_sensor, (select username from User where id = Project.owner limit 1) as owner
            from Project
            where active_sensor = ?;
            ''',
            (sensor_id,)
        )
        proj_cursor.row_factory = cls.row_factory
        return proj_cursor.fetchone()

    def as_link(self):
        if self.active_sensor:
            # TODO(tr) build sensor object in Project object on query
            sensor = get_sensor(self.active_sensor)
            last_active = sensor.last_active_str()
            sensor_state = sensor.get_state()
        else:
            last_active = 'Inactive'
            sensor_state = SensorState.INACTIVE

        return {
            'link': url_for('accessor.get_project', project_id=self.id),
            'label': self.name or '<deleted>',
            'owner': self.owner,
            'last_active': last_active,
            'sensor_state': sensor_state,
        }

    def attach_sensor(self, db_conn, sensor_id=None):
        # type: (SQLConnection, Optional[int]) -> None
        """
        Update the active sensor of a project. If None is provided as a sensor id then only detach
        the current sensor.
        """

        if sensor_id is not None:
            # Remove the sensor from any projects its currently attached to.
            db_conn.execute(
                '''
                update Project set active_sensor = null
                where active_sensor = ?;
                ''',
                (sensor_id,)
            )
            db_conn.execute(
                '''
                update Project set active_sensor = ?
                where id = ?;
                ''',
                (sensor_id, self.id)
            )
        else:
            db_conn.execute(
                '''
                update Project set active_sensor = null
                where id = ?;
                ''',
                (self.id,)
            )

    @classmethod
    def create_new(cls, db_conn, name, owner):
        # type: (SQLConnection, AnyStr, Int) -> int
        cursor = db_conn.cursor()
        cursor.execute(
            '''
            insert into Project (name, owner) values (?, ?);
            ''',
            (name,owner)
        )
        # lastrowid is the last successful insert on that cursor
        return cursor.lastrowid


@attr.s
class DataPoints:
    sensor_id = attr.ib(type=int)
    project_id = attr.ib(type=int)
    timestamp = attr.ib(type=datetime)
    angle = attr.ib(type=float)
    temperature = attr.ib(type=float)
    battery = attr.ib(type=float)
    id = attr.ib(type=int, default=None)

    def timestamp_as_str(self):
        # type: () -> str
        if self.timestamp:
            return self.timestamp.isoformat()
        return 'no data'

    def temperature_as_str(self):
        return f'{self.temperature:2.1f}'

    def gravity_as_str(self):
        return f'{self.gravity:1.3f}'

    def battery_as_str(self):
        # TODO(tr) Use calibration to know that.
        return f'{self.battery:2.2f}'

    def angle_as_str(self):
        return f'{self.angle:3.1f}'

    @property
    def gravity(self):
        # TODO(tr) Use an actual algorithm with the sensor's config to convert
        # Transforms 45 to 1.045
        return 1.0 + self.angle / 1000

    def as_datatable(self):
        return {
            'when': {
                'label': self.timestamp_as_str(),
                'timestamp': self.timestamp.timestamp()
            },
            'gravity': self.gravity_as_str(),
            'angle': self.angle_as_str(),
            'temperature': self.temperature_as_str(),
            'battery': self.battery_as_str(),
        }

    @classmethod
    def row_factory(cls, _cursor, _row):
        d = {}
        for idx, col in enumerate(_cursor.description):
            d[col[0]] = _row[idx]
        return cls(
            d['sensor_id'],
            d['project_id'],
            datetime.fromisoformat(d['timestamp']),
            d['angle'],
            d['temperature'],
            d['battery'],
            d['id'],
        )

    @classmethod
    def get_all(cls, db_conn, project_id=None, sensor_id=None):
        # type: (SQLConnection, Optional[int], Optional[int]) -> List[DataPoints]
        if project_id is not None:
            data_cursor = db_conn.execute(
                '''
                select id, project_id, sensor_id, angle, temperature, battery, timestamp
                from Datapoint
                where project_id = ?;
                ''',
                (project_id,)
            )
        elif sensor_id is not None:
            data_cursor = db_conn.execute(
                '''
                select id, project_id, sensor_id, angle, temperature, battery, timestamp
                from Datapoint
                where sensor_id = ?;
                ''',
                (sensor_id,)
            )
        else:
            raise NotImplementedError
        data_cursor.row_factory = DataPoints.row_factory
        return data_cursor.fetchall()


@attr.s
class ProjectData(Project):
    sensors = attr.ib(default=attr.Factory(dict))  # type: Dict[int, Sensor]
    data_points = attr.ib(default=attr.Factory(list))  # type: List[DataPoints]

    @classmethod
    def get_data(cls, db_conn, project_id):
        # type: (SQLConnection, int) -> Optional[ProjectData]
        project_data = cls.find(db_conn, project_id)
        if not project_data:
            return

        sensor_ids = set()
        for row in DataPoints.get_all(db_conn, project_id):
            project_data.data_points.append(row)
            sensor_ids.add(row.sensor_id)

        # TODO(tr) do a sensor_id in []
        # TODO(tr) ensure the active sensor is first?
        for _id in sensor_ids:
            sensor = Sensor.find(db_conn, _id)
            if sensor is not None:
                project_data.sensors[_id] = sensor

        return project_data


@attr.s
class SensorData(Sensor):
    projects = attr.ib(default=attr.Factory(dict))  # type: Dict[int, Project]
    data_points = attr.ib(default=attr.Factory(list))  # type: List[DataPoints]

    @classmethod
    def get_data(cls, db_conn, sensor_id):
        # type: (SQLConnection, int) -> Optional[SensorData]
        sensor_data = cls.find(db_conn, sensor_id)
        if not sensor_data:
            return

        project_ids = set()
        for row in DataPoints.get_all(db_conn, sensor_id=sensor_id):
            sensor_data.data_points.append(row)
            project_ids.add(row.project_id)

        # TODO(tr) Do a proper select id in []
        for _id in project_ids:
            project = Project.find(db_conn, _id)
            if project is not None:
                sensor_data.projects[_id] = project

        return sensor_data


def get_projects():
    # type: () -> List[Project]
    with config().db_connection() as db_conn:
        return Project.get_all(db_conn)


def get_sensors():
    # type: () -> List[Sensor]
    with config().db_connection() as db_conn:
        return Sensor.get_all(db_conn)


def get_sensor(sensor_id):
    # type: (int) -> Optional[Sensor]
    with config().db_connection() as db_conn:
        return Sensor.find(db_conn, sensor_id)


def get_active_project_for_sensor(sensor_id):
    # type: (int) -> Tuple[Optional[Sensor], Optional[Project]]
    with config().db_connection() as db_conn:
        return Sensor.find(db_conn, sensor_id), ProjectData.by_active_sensor(db_conn, sensor_id)


def insert_datapoints(datapoints):
    # type: (List[DataPoints]) -> None
    with config().db_connection() as db_conn:
        db_conn.executemany(
            '''
            insert into Datapoint (sensor_id, project_id, timestamp, angle, temperature, battery)
            values (?, ?, datetime(?), ?, ?, ?);
            ''',
            [
                (d.sensor_id, d.project_id, d.timestamp, d.angle, d.temperature, d.battery)
                for d in datapoints
            ]
        )


def get_project_data(project_id):
    # type: (int) -> Optional[ProjectData]
    with config().db_connection() as db_conn:
        return ProjectData.get_data(db_conn, project_id)


def get_sensor_data(sensor_id):
    # type: (int) -> Optional[SensorData]
    with config().db_connection() as db_conn:
        return SensorData.get_data(db_conn, sensor_id)


def insert_project(name, owner):
    # type: (AnyStr, Int) -> int
    with config().db_connection() as db_conn:
        return Project.create_new(db_conn, name, owner)


def insert_sensor(name, secret, owner):
    # type: (AnyStr, AnyStr, Int) -> int
    with config().db_connection() as db_conn:
        return Sensor.create_new(db_conn, name, secret, owner)


def update_project_sensor(project, sensor_id=None):
    # type: (Project, Optional[int]) -> None
    with config().db_connection() as db_conn:
        project.attach_sensor(db_conn, sensor_id)


def remove_datapoint(datapoint_id):
    # type: (int) -> None
    with config().db_connection() as db_conn:
        db_conn.execute(
            '''
            delete from Datapoint
            where id = ?;
            ''',
            (datapoint_id,)
        )
