from datetime import datetime, timedelta
from typing import Dict, List, Optional, AnyStr, Tuple

import attr
from flask import url_for

from brewmonitor.configuration import SQLConnection, config


# Assumes children classes will use attr.s
from brewmonitor.user import User


class BaseTable:
    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return []

    @classmethod
    def create_table_req(cls) -> str:
        rv = []

        for f in attr.fields(cls):  # type: attr.Attribute
            if f.metadata and 'sql' in f.metadata:
                rv.append(f.metadata['sql'].format(name=f.name))

        rv += cls.additional_sql_fields()

        return f"create table if not exists {cls.__name__} (" + ', '.join(rv) + ");"


@attr.s
class Sensor(BaseTable):
    id = attr.ib(type=int, metadata={'sql': '{name} integer primary key autoincrement'})
    name = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    secret = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    owner = attr.ib(type=str, metadata={'sql': '{name} integer not null'})
    max_battery = attr.ib(type=float, default=None, metadata={'sql': '{name} real'})
    min_battery = attr.ib(type=float, default=None, metadata={'sql': '{name} real'})

    last_active = attr.ib(type=datetime, default=None)  # in SQL we get that from the datapoints
    last_battery = attr.ib(type=float, default=None)  # in SQL we get that from the datapoints
    linked_project = attr.ib(type=int, default=None)  # Assuming a sensor is only attached to 1 project

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return [
            'battery float',
            'foreign key(owner) references User(id)',
        ]

    @classmethod
    def row_factory(cls, _cursor, _row) -> "Sensor":
        d = {
            col[0]: _row[idx]
            for idx, col in enumerate(_cursor.description)
        }
        return cls(
            d['id'],
            d['name'],
            d['secret'],
            d['owner'],
            d['max_battery'],
            d['min_battery'],
            last_active=datetime.fromisoformat(d['last_active']) if d['last_active'] else None,
            last_battery=d['last_battery'],
            linked_project=d['linked_project'],
        )

    @classmethod
    def get_all(cls, db_conn: SQLConnection) -> List["Sensor"]:
        cursor = db_conn.execute(
            '''
            select id, name, secret, max_battery, min_battery, 
                (select battery from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1) as last_battery,
                (select timestamp from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1) as last_active,
                (select username from User where id = Sensor.owner limit 1) as owner,
                (select id from Project where active_sensor = Sensor.id) as linked_project
            from Sensor
            order by id desc;
            '''
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn: SQLConnection, sensor_id: int) -> Optional["Sensor"]:
        sens_cursor = db_conn.execute(
            '''
            select id, name, secret, max_battery, min_battery, 
                (select battery from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1) as last_battery,
                (select timestamp from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1) as last_active,
                (select username from User where id = Sensor.owner limit 1) as owner,
                (select id from Project where active_sensor = Sensor.id) as linked_project
            from Sensor where id = ?;
            ''',
            (sensor_id,)
        )
        sens_cursor.row_factory = cls.row_factory
        return sens_cursor.fetchone()

    @classmethod
    def create(cls, db_conn: SQLConnection, name: AnyStr, secret: AnyStr, owner: User) -> "Sensor":
        cursor = db_conn.cursor()
        cursor.execute(
            '''
            insert into Sensor (name, secret, owner) values (?, ?, ?);
            ''',
            (name, secret, owner.id),
        )
        # lastrowid is the last successful insert on that cursor
        return cls(cursor.lastrowid, name, secret, owner.name)

    @classmethod
    def edit(
        cls,
        db_conn: SQLConnection,
        s_id: int,
        new_name: AnyStr,
        new_secret: AnyStr,
        new_owner_id: int,
        new_max_battery: int,
        new_min_battery: int,
    ):
        db_conn.execute(
            """
            Update Sensor
            set name=?, secret=?, owner=?, max_battery=?, min_battery=?
            where id=?;
            """,
            (new_name, new_secret, new_owner_id, new_max_battery, new_min_battery, s_id),
        )

    @classmethod
    def delete(cls, db_conn: SQLConnection, s_id: int):
        db_conn.execute(
            """
            Delete from Datapoint where sensor_id=?;
            """,
            (s_id,),
        )
        db_conn.execute(
            """
            Update Project set 'active_sensor' = NULL where active_sensor=?;
            """,
            (s_id,),
        )
        db_conn.execute(
            """
            Delete from Sensor where id=?;
            """,
            (s_id,),
        )

    def last_active_str(self) -> str:
        if self.last_active is not None:
            return self.last_active.isoformat()
        return 'No data'

    def last_battery_pct(self) -> Optional[int]:
        if self.last_battery is not None and self.max_battery is not None and self.min_battery is not None:
            if self.last_battery > self.max_battery:
                return 100
            if self.last_battery < self.min_battery:
                return 0
            return int(((self.last_battery - self.min_battery)*100) / (self.max_battery - self.min_battery))
        return None
    
    def battery_info(self) -> Dict:
        value = self.last_battery_pct()
        if value is None:
            label = 'Unknown battery state'
            icon = 'fa-question'
        else:
            label = f'{value}%'
            if value > 80:
                icon = 'fa-battery-full'
            elif value > 60:
                icon = 'fa-battery-three-quarters'
            elif value > 40:
                icon = 'fa-battery-half'
            elif value > 20:
                icon = 'fa-battery-quarter'
            else:
                icon = 'fa-battery-empty'
        return {
            'value': value,
            'tooltip': label,
            'icon': icon,
        }

    def is_linked(self) -> bool:
        return bool(self.linked_project)

    def get_link(self) -> str:
        return url_for('accessor.get_sensor', sensor_id=self.id)

    def get_name(self) -> str:
        return self.name or '<deleted>'

    def is_active(self) -> bool:
        return self.last_active is not None and datetime.now() - self.last_active < timedelta(days=1)

    def verify_identity(self, request_secret: str) -> bool:
        # Return true if the secret provided by the request matches the sensor's secret from the db
        return self.secret == request_secret


@attr.s
class Project(BaseTable):
    id = attr.ib(type=int, metadata={'sql': '{name} integer primary key autoincrement'})
    name = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    owner = attr.ib(type=int, metadata={'sql': '{name} integer not null'})
    # Assuming 1 sensor per project but could change the sensor.
    active_sensor = attr.ib(type=int, default=None, metadata={'sql': '{name} integer'})

    first_active = attr.ib(type=datetime, default=None)  # in SQL we would get that from the datapoints
    last_active = attr.ib(type=datetime, default=None)  # in SQL we would get that from the datapoints
    first_angle = attr.ib(type=float, default=None)
    last_angle = attr.ib(type=float, default=None)
    last_temperature = attr.ib(type=float, default=None)

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return [
            'foreign key(owner) references User(id)',
            'foreign key(active_sensor) references Sensor(id)',
        ]

    @classmethod
    def row_factory(cls, _cursor, _row) -> "Project":
        d = {
            col[0]: _row[idx]
            for idx, col in enumerate(_cursor.description)
        }
        return cls(
            d['id'],
            d['name'],
            d['owner'],
            d['active_sensor'],
            datetime.fromisoformat(d['first_active']) if d['first_active'] else None,
            datetime.fromisoformat(d['last_active']) if d['last_active'] else None,
            d['first_angle'],
            d['last_angle'],
            d['last_temperature'],
        )

    @classmethod
    def get_all(cls, db_conn: SQLConnection) -> List["Project"]:
        cursor = db_conn.execute(
            '''
            select id, name, active_sensor, 
                (select timestamp from Datapoint where project_id = Project.id order by timestamp asc limit 1) as first_active, 
                (select timestamp from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_active, 
                (select angle from Datapoint where project_id = Project.id order by timestamp asc limit 1) as first_angle, 
                (select angle from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_angle, 
                (select temperature from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_temperature, 
                (select username from User where id = Project.owner limit 1) as owner
            from Project
            order by id desc;
            '''
        )
        # TODO(tr) Add order by last activity
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn: SQLConnection, project_id: int) -> "Project":
        cursor = db_conn.execute(
            '''
            select id, name, active_sensor, 
                (select timestamp from Datapoint where project_id = Project.id order by timestamp asc limit 1) as first_active, 
                (select timestamp from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_active, 
                (select angle from Datapoint where project_id = Project.id order by timestamp asc limit 1) as first_angle, 
                (select angle from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_angle, 
                (select temperature from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_temperature, 
                (select username from User where id = Project.owner limit 1) as owner
            from Project
            where id = ?;
            ''',
            (project_id,)
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchone()

    @classmethod
    def by_active_sensor(cls, db_conn: SQLConnection, sensor_id: int) -> Optional["Project"]:
        proj_cursor = db_conn.execute(
            '''
            select id, name, active_sensor, 
                (select timestamp from Datapoint where project_id = Project.id order by timestamp asc limit 1) as first_active, 
                (select timestamp from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_active, 
                (select angle from Datapoint where project_id = Project.id order by timestamp asc limit 1) as first_angle, 
                (select angle from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_angle, 
                (select temperature from Datapoint where project_id = Project.id order by timestamp desc limit 1) as last_temperature, 
                (select username from User where id = Project.owner limit 1) as owner
            from Project
            where active_sensor = ?
            order by id desc;
            ''',
            (sensor_id,)
        )
        proj_cursor.row_factory = cls.row_factory
        return proj_cursor.fetchone()

    @classmethod
    def delete(cls, db_conn: SQLConnection, p_id: int):
        db_conn.execute(
            """
            Delete from Datapoint where project_id=?;
            """,
            (p_id,)
        )
        db_conn.execute(
            """
            Delete from Project where id=?;
            """,
            (p_id,)
        )

    @classmethod
    def edit(cls, db_conn: SQLConnection, p_id: int, new_name: AnyStr, new_owner_id: int):
        db_conn.execute(
            """
            Update Project
            set name=?, owner=?
            where id=?;
            """,
            (new_name, new_owner_id, p_id),
        )

    @classmethod
    def create(cls, db_conn: SQLConnection, name: AnyStr, owner_id: int) -> "Project":
        cursor = db_conn.cursor()
        cursor.execute(
            '''
            insert into Project (name, owner) values (?, ?);
            ''',
            (name, owner_id),
        )
        # lastrowid is the last successful insert on that cursor
        return cls(cursor.lastrowid, name, owner_id)

    def last_active_str(self) -> str:
        if self.last_active is not None:
            return self.last_active.isoformat()
        return 'No data'

    def is_linked(self) -> bool:
        return bool(self.active_sensor)

    def get_link(self) -> str:
        return url_for('accessor.get_project', project_id=self.id)

    def get_name(self) -> str:
        return self.name or '<deleted>'

    def is_active(self) -> bool:
        return self.last_active is not None and datetime.now() - self.last_active < timedelta(days=1)

    def attach_sensor(self, db_conn: SQLConnection, sensor_id: Optional[int] = None) -> None:
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
                (sensor_id,),
            )
            db_conn.execute(
                '''
                update Project set active_sensor = ?
                where id = ?;
                ''',
                (sensor_id, self.id),
            )
        else:
            db_conn.execute(
                '''
                update Project set active_sensor = null
                where id = ?;
                ''',
                (self.id,),
            )


@attr.s
class Datapoint(BaseTable):
    sensor_id = attr.ib(type=int, metadata={'sql': '{name} integer not null'})
    project_id = attr.ib(type=int, metadata={'sql': '{name} integer'})
    timestamp = attr.ib(type=datetime, metadata={'sql': '{name} integer not null'})
    angle = attr.ib(type=float, metadata={'sql': '{name} real'})
    temperature = attr.ib(type=float, metadata={'sql': '{name} real'})
    battery = attr.ib(type=float, metadata={'sql': '{name} real'})
    id = attr.ib(type=int, default=None, metadata={'sql': '{name} integer primary key autoincrement'})

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return [
            'foreign key(sensor_id) references Sensor(id)',
            'foreign key(project_id) references Project(id)',
        ]

    @classmethod
    def create_many(cls, conn: SQLConnection, datapoints: List["Datapoint"]):
        conn.executemany(
            '''
            insert into Datapoint (sensor_id, project_id, timestamp, angle, temperature, battery)
            values (?, ?, datetime(?), ?, ?, ?);
            ''',
            [
                (d.sensor_id, d.project_id, d.timestamp, d.angle, d.temperature, d.battery)
                for d in datapoints
            ]
        )

    def timestamp_as_str(self) -> str:
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
    def get_all(
        cls,
        db_conn: SQLConnection,
        project_id: Optional[int] = None,
        sensor_id: Optional[int] = None,
    ) -> List["Datapoint"]:
        if project_id is not None:
            data_cursor = db_conn.execute(
                '''
                select id, project_id, sensor_id, angle, temperature, battery, timestamp
                from Datapoint
                where project_id = ?;
                ''',
                (project_id,),
            )
        elif sensor_id is not None:
            data_cursor = db_conn.execute(
                '''
                select id, project_id, sensor_id, angle, temperature, battery, timestamp
                from Datapoint
                where sensor_id = ?;
                ''',
                (sensor_id,),
            )
        else:
            # Needs either a project or a sensor id.
            raise NotImplementedError
        data_cursor.row_factory = Datapoint.row_factory
        return data_cursor.fetchall()


@attr.s
class ProjectData(Project):
    sensors = attr.ib(type=dict, default=attr.Factory(dict))  # type: Dict[int, Sensor]
    data_points = attr.ib(type=list, default=attr.Factory(list))  # type: List[Datapoint]

    @classmethod
    def get_data(cls, db_conn: SQLConnection, project_id: int) -> Optional["ProjectData"]:
        project_data = cls.find(db_conn, project_id)
        if not project_data:
            return

        sensor_ids = set()
        for row in Datapoint.get_all(db_conn, project_id):
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
    projects = attr.ib(type=dict, default=attr.Factory(dict))  # type: Dict[int, Project]
    data_points = attr.ib(type=list, default=attr.Factory(list))  # type: List[Datapoint]

    @classmethod
    def get_data(cls, db_conn: SQLConnection, sensor_id: int) -> Optional["SensorData"]:
        sensor_data = cls.find(db_conn, sensor_id)
        if not sensor_data:
            return

        project_ids = set()
        for row in Datapoint.get_all(db_conn, sensor_id=sensor_id):
            sensor_data.data_points.append(row)
            project_ids.add(row.project_id)

        # TODO(tr) Do a proper select id in []
        for _id in project_ids:
            project = Project.find(db_conn, _id)
            if project is not None:
                sensor_data.projects[_id] = project

        return sensor_data


def get_projects() -> List[Project]:
    with config().db_connection() as db_conn:
        return Project.get_all(db_conn)


def get_sensors() -> List[Sensor]:
    with config().db_connection() as db_conn:
        return Sensor.get_all(db_conn)


def get_sensor(sensor_id: int) -> Optional[Sensor]:
    with config().db_connection() as db_conn:
        return Sensor.find(db_conn, sensor_id)


def get_active_project_for_sensor(sensor_id: int) -> Tuple[Optional[Sensor], Optional[Project]]:
    with config().db_connection() as db_conn:
        return Sensor.find(db_conn, sensor_id), ProjectData.by_active_sensor(db_conn, sensor_id)


def insert_datapoints(datapoints: List[Datapoint]):
    with config().db_connection() as db_conn:
        Datapoint.create_many(db_conn, datapoints)


def get_project_data(project_id: int) -> Optional[ProjectData]:
    with config().db_connection() as db_conn:
        return ProjectData.get_data(db_conn, project_id)


def get_sensor_data(sensor_id: int) -> Optional[SensorData]:
    with config().db_connection() as db_conn:
        return SensorData.get_data(db_conn, sensor_id)


def insert_project(name: AnyStr, owner_id: int) -> Project:
    with config().db_connection() as db_conn:
        return Project.create(db_conn, name, owner_id)


def insert_sensor(name: AnyStr, secret: AnyStr, owner: User) -> Sensor:
    with config().db_connection() as db_conn:
        return Sensor.create(db_conn, name, secret, owner)


def update_project_sensor(project: Project, sensor_id: Optional[int] = None) -> None:
    with config().db_connection() as db_conn:
        project.attach_sensor(db_conn, sensor_id)


def remove_datapoint(datapoint_id: int):
    with config().db_connection() as db_conn:
        db_conn.execute(
            '''
            delete from Datapoint
            where id = ?;
            ''',
            (datapoint_id,)
        )
