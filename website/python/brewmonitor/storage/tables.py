import abc
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

import attr
import bcrypt
from brewmonitor.configuration import SQLConnection
from flask import url_for
from flask_login import UserMixin


# This is to use in kwargs that are required but have need a default
# for inheritance purposes.
Required = None


class BaseTable(metaclass=abc.ABCMeta):
    # Assumes children classes will use attr.s
    # Each attributes can defined metadata.db_factory: Callable[[Dict], Any] to get a row
    # and transform it to the expected object in python from the db value.

    def __init__(self, *args, **kwargs):
        super().__init__()

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

        return f'create table if not exists {cls.__name__} ({", ".join(rv)});'

    @classmethod
    def row_factory_as_dict(cls, cursor, row) -> Dict:
        """
        Help extract entries from the cursor and use default field values if
        not in the request.
        """
        d = {
            col[0]: row[idx]
            for idx, col in enumerate(cursor.description)
        }
        for field in attr.fields(cls):  # type: attr.Attribute
            if field.name not in d:
                if isinstance(field.default, attr.Factory):
                    d[field.name] = field.default.factory()
                elif field.default is not attr.NOTHING:
                    d[field.name] = field.default
            elif field.metadata.get('db_factory'):
                d[field.name] = field.metadata['db_factory'](d)

        return d

    @classmethod
    def sub_fields(cls) -> List[str]:
        """Helper method to extract sub-querries from attr fields"""
        return [
            f'({f.metadata["subquery"]}) as {f.name}'
            for f in attr.fields(cls)  # type: attr.Attribute
            if f.metadata.get('subquery')
        ]

    @classmethod
    def row_factory(cls, cursor, row) -> 'BaseTable':
        return cls(**cls.row_factory_as_dict(cursor, row))

    @classmethod
    @abc.abstractmethod
    def get_all(cls, db_conn: SQLConnection, **kwargs) -> List:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def find(cls, db_conn: SQLConnection, **kwargs) -> Optional:
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def create(cls, db_conn: SQLConnection, **kwargs) -> 'BaseTable':
        raise NotImplementedError()

    @abc.abstractmethod
    def edit(self, db_conn: SQLConnection, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, db_conn: SQLConnection):
        raise NotImplementedError()


def datetime_row_factory(field_name: str) -> Callable[[Dict], Optional[datetime]]:
    def _f(r: Dict) -> Optional[datetime]:
        return datetime.fromisoformat(r[field_name]) if r[field_name] else None
    return _f


@attr.s
class User(BaseTable, UserMixin):
    id = attr.ib(type=int, metadata={'sql': '{name} integer primary key autoincrement'})
    username = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    is_admin = attr.ib(type=bool, metadata={'sql': '{name} bool', 'db_factory': lambda r: bool(r['is_admin'])})

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return super(User, cls).additional_sql_fields() + [
            'password text not null',
        ]

    @classmethod
    def get_all(cls, db_conn: SQLConnection, **kwargs) -> List:
        if kwargs:
            raise ValueError('Not args required.')

        cursor = db_conn.execute(
            """
            select id, username, is_admin from User;
            """,
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn: SQLConnection, user_id: int = Required) -> Optional['User']:
        if user_id is None:
            raise ValueError('user_id is required')

        cursor = db_conn.execute(
            """
            select id, username, is_admin
            from User
            where id=?;
            """,
            (user_id,),
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchone()

    @classmethod
    def create(
        cls,
        db_conn: SQLConnection,
        username: str = Required,
        password: str = Required,
        is_admin: bool = Required,
    ) -> 'User':
        if username is None or password is None or is_admin is None:
            raise ValueError('All args are required.')

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
        cursor = db_conn.cursor()

        cursor.execute(
            """
            insert into User (username, password, is_admin)
            values (?, ?, ?);
            """,
            (username, hashed_password, is_admin),
        )
        # lastrowid is the last successful insert on that cursor
        return cls(cursor.lastrowid, username, is_admin)

    def delete(self, db_conn: SQLConnection):
        # TODO(tr) Do we need to remove the owner from the Project?
        #  Or have a <deleted> user to re-attach them to?
        db_conn.execute(
            """
            delete from User where id=?;
            """,
            (self.id,),
        )

    def edit(self, db_conn: SQLConnection, **kwargs):
        raise RuntimeError()

    @classmethod
    def verify(cls, db_conn: SQLConnection, username: str, password: str) -> Optional['User']:
        data = db_conn.execute(
            """
            select id, is_admin, password
            from User
            where username = ?;
            """,
            (username,),
        ).fetchone()

        if data is not None:
            hashed_password = data[2]
            if bcrypt.checkpw(password.encode('utf8'), hashed_password):
                return cls(
                    data[0],
                    username,
                    data[1],
                )
        return None


@attr.s
class Sensor(BaseTable):
    id = attr.ib(type=int, metadata={'sql': '{name} integer primary key autoincrement'})
    name = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    secret = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    # TODO(tr) This should really be the owner id and we should store the name separately
    owner = attr.ib(
        type=str,
        metadata={
            'sql': '{name} integer not null',
            'subquery': """select username from User where id = Sensor.owner limit 1""",
        },
    )
    max_battery = attr.ib(type=float, default=2.0, metadata={'sql': '{name} real'})
    min_battery = attr.ib(type=float, default=4.0, metadata={'sql': '{name} real'})

    last_active = attr.ib(
        type=datetime,
        default=None,
        metadata={
            'db_factory': datetime_row_factory('last_active'),
            'subquery': """
                select battery from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1
            """,
        },
    )
    last_battery = attr.ib(
        type=float,
        default=None,
        metadata={
            'subquery': """
                select battery from Datapoint where sensor_id = Sensor.id order by timestamp desc limit 1
            """,
        },
    )
    linked_project = attr.ib(
        type=int,
        default=None,
        metadata={
            'subquery': """select id from Project where active_sensor = Sensor.id""",
        },
    )  # Assuming a sensor is only attached to 1 project

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return super(Sensor, cls).additional_sql_fields() + [
            'battery float',
            'foreign key(owner) references User(id)',
        ]

    @classmethod
    def get_all(cls, db_conn: SQLConnection, **kwargs) -> List['Sensor']:
        cursor = db_conn.execute(
            f"""
            select id, name, secret, max_battery, min_battery, {", ".join(cls.sub_fields())}
            from Sensor
            order by id desc;
            """,
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn: SQLConnection, sensor_id: int = Required) -> Optional['Sensor']:
        if sensor_id is None:
            raise ValueError('sensor_id is required')
        sens_cursor = db_conn.execute(
            f"""
            select id, name, secret, max_battery, min_battery, {", ".join(cls.sub_fields())}
            from Sensor where id = ?;
            """,
            (sensor_id,),
        )
        sens_cursor.row_factory = cls.row_factory
        return sens_cursor.fetchone()

    @classmethod
    def create(
        cls,
        db_conn: SQLConnection,
        name: str = Required,
        secret: str = Required,
        owner: User = Required,
        min_battery: float = None,
        max_battery: float = None,
    ) -> 'Sensor':
        if name is None or secret is None or owner is None:
            raise ValueError('Most arguments are required')

        default_val = attr.fields_dict(cls)

        if min_battery is None and default_val['min_battery'].default is not attr.NOTHING:
            min_battery = default_val['min_battery'].default
        if max_battery is None and default_val['max_battery'].default is not attr.NOTHING:
            max_battery = default_val['max_battery'].default

        cursor = db_conn.cursor()
        cursor.execute(
            """
            insert into Sensor
            (name, secret, owner, max_battery, min_battery)
            values (?, ?, ?, ?, ?);
            """,
            (name, secret, owner.id, min_battery, max_battery),
        )
        # lastrowid is the last successful insert on that cursor
        return cls(cursor.lastrowid, name, secret, owner.username, min_battery, max_battery)

    def edit(self, db_conn: SQLConnection, **kwargs):
        request_fields = []
        request_content = []
        attrs_to_change = {}

        for a in ('name', 'secret', 'max_battery', 'min_battery'):
            if a in kwargs:
                request_fields.append(f'{a}=?')
                v = kwargs.pop(a)
                request_content.append(v)
                attrs_to_change[a] = v

        if 'owner' in kwargs:
            new_owner = kwargs.pop('owner')
            request_fields.append('owner=?')
            request_content.append(new_owner.id)
            attrs_to_change['owner'] = new_owner.username

        if kwargs:
            raise ValueError(f'Unexpected kwargs: {sorted(kwargs.keys())}')

        request_content.append(self.id)

        db_conn.execute(
            f"""
            update Sensor set {', '.join(request_fields)} where id=?;
            """,
            request_content,
        )
        # Change the object only when the SQL was done
        for k, v in attrs_to_change.items():
            setattr(self, k, v)

    def delete(self, db_conn: SQLConnection):
        """Cascade deletion of the sensor.
        Removes Datapoint entries and detach from active Project.
        """
        db_conn.execute(
            """
            delete from Datapoint where sensor_id=?;
            """,
            (self.id,),
        )
        db_conn.execute(
            """
            update Project set 'active_sensor' = NULL where active_sensor=?;
            """,
            (self.id,),
        )
        db_conn.execute(
            """
            delete from Sensor where id=?;
            """,
            (self.id,),
        )

    def get_label(self) -> str:
        return self.name or '<deleted>'

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
            return int(((self.last_battery - self.min_battery) * 100) / (self.max_battery - self.min_battery))
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

    def is_active(self) -> bool:
        return self.last_active is not None and datetime.now() - self.last_active < timedelta(days=1)

    def verify_identity(self, request_secret: str) -> bool:
        # Return true if the secret provided by the request matches the sensor's
        # secret from the db
        return self.secret == request_secret


@attr.s
class Project(BaseTable):
    id = attr.ib(type=int, metadata={'sql': '{name} integer primary key autoincrement'})
    name = attr.ib(type=str, metadata={'sql': '{name} text not null'})
    # TODO(tr) This should really be the owner id and we should store the name separately
    owner = attr.ib(
        type=str,
        metadata={
            'sql': '{name} integer not null',
            'subquery': """select username from User where id = Project.owner limit 1""",
        },
    )
    # Assuming 1 sensor per project but could change the sensor.
    active_sensor = attr.ib(type=int, default=None, metadata={'sql': '{name} integer'})

    first_active = attr.ib(
        type=datetime,
        default=None,
        metadata={
            'db_factory': datetime_row_factory('first_active'),
            'subquery': """
                select timestamp from Datapoint where project_id = Project.id order by timestamp asc limit 1
            """,
        },
    )  # in SQL we would get that from the datapoints
    last_active = attr.ib(
        type=datetime,
        default=None,
        metadata={
            'db_factory': datetime_row_factory('last_active'),
            'subquery': """
                select timestamp from Datapoint where project_id = Project.id order by timestamp desc limit 1
            """,
        },
    )  # in SQL we would get that from the datapoints
    first_angle = attr.ib(
        type=float,
        default=None,
        metadata={
            'subquery': """
                select angle from Datapoint where project_id = Project.id order by timestamp asc limit 1
            """,
        },
    )
    last_angle = attr.ib(
        type=float,
        default=None,
        metadata={
            'subquery': """
                select angle from Datapoint where project_id = Project.id order by timestamp desc limit 1
            """,
        },
    )
    last_temperature = attr.ib(
        type=float,
        default=None,
        metadata={
            'subquery': """
                select temperature from Datapoint where project_id = Project.id order by timestamp desc limit 1
            """,
        },
    )

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return super(Project, cls).additional_sql_fields() + [
            'foreign key(owner) references User(id)',
            'foreign key(active_sensor) references Sensor(id)',
        ]

    @classmethod
    def get_all(cls, db_conn: SQLConnection, **kwargs) -> List['Project']:
        if kwargs:
            raise ValueError('No parameters are required')

        cursor = db_conn.execute(
            f"""
            select id, name, active_sensor, {", ".join(cls.sub_fields())}
            from Project
            order by id desc;
            """,
        )
        # TODO(tr) Add order by last activity
        cursor.row_factory = cls.row_factory
        return cursor.fetchall()

    @classmethod
    def find(cls, db_conn: SQLConnection, project_id: int = Required) -> Optional['Project']:
        if project_id is None:
            raise ValueError('project_id is required')

        cursor = db_conn.execute(
            f"""
            select id, name, active_sensor, {", ".join(cls.sub_fields())}
            from Project
            where id = ?;
            """,
            (project_id,),
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchone()

    @classmethod
    def by_active_sensor(cls, db_conn: SQLConnection, sensor_id: int) -> Optional['Project']:
        proj_cursor = db_conn.execute(
            f"""
            select id, name, active_sensor, {", ".join(cls.sub_fields())}
            from Project
            where active_sensor = ?
            order by id desc;
            """,
            (sensor_id,),
        )
        proj_cursor.row_factory = cls.row_factory
        return proj_cursor.fetchone()

    @classmethod
    def create(cls, db_conn: SQLConnection, name: str = Required, owner: User = Required) -> 'Project':
        if name is None or owner is None:
            raise ValueError('All args are required')

        cursor = db_conn.cursor()
        cursor.execute(
            """
            insert into Project (name, owner) values (?, ?);
            """,
            (name, owner.id),
        )
        # lastrowid is the last successful insert on that cursor
        return cls(cursor.lastrowid, name, owner.username)

    def delete(self, db_conn: SQLConnection):
        """Cascade deletion of the Project (removes all entries fro Datapoint too)."""
        db_conn.execute(
            """
            delete from Datapoint where project_id=?;
            """,
            (self.id,),
        )
        db_conn.execute(
            """
            delete from Project where id=?;
            """,
            (self.id,),
        )

    def edit(self, db_conn: SQLConnection, name: str = Required, owner: User = Required):
        if name is None or owner is None:
            raise ValueError('All args are required')

        db_conn.execute(
            """
            update Project
            set name=?, owner=?
            where id=?;
            """,
            (name, owner.id, self.id),
        )
        self.name = name
        self.owner = owner.username

    def get_label(self) -> str:
        return self.name or '<deleted>'

    def last_active_str(self) -> str:
        if self.last_active is not None:
            return self.last_active.isoformat()
        return 'No data'

    def is_linked(self) -> bool:
        return bool(self.active_sensor)

    def get_link(self) -> str:
        return url_for('accessor.get_project', project_id=self.id)

    def is_active(self) -> bool:
        return self.last_active is not None and datetime.now() - self.last_active < timedelta(days=1)

    def attach_sensor(self, db_conn: SQLConnection, sensor_id: Optional[int] = None) -> None:
        """
        Update the active sensor of a project.
        If None is provided as a sensor id then only detach the current sensor.
        """
        # TODO(tr) check self.active_sensor != sensor_id?

        if sensor_id is not None:
            # Remove the sensor from any projects its currently attached to.
            db_conn.execute(
                """
                update Project set active_sensor = null
                where active_sensor = ?;
                """,
                (sensor_id,),
            )
            db_conn.execute(
                """
                update Project set active_sensor = ?
                where id = ?;
                """,
                (sensor_id, self.id),
            )
        else:
            db_conn.execute(
                """
                update Project set active_sensor = null
                where id = ?;
                """,
                (self.id,),
            )
        self.active_sensor = sensor_id


@attr.s
class Datapoint(BaseTable):
    sensor_id = attr.ib(type=int, metadata={'sql': '{name} integer not null'})
    project_id = attr.ib(type=int, metadata={'sql': '{name} integer'})
    timestamp = attr.ib(
        type=datetime,
        metadata={'sql': '{name} integer not null', 'db_factory': datetime_row_factory('timestamp')},
    )
    angle = attr.ib(type=float, metadata={'sql': '{name} real'})
    temperature = attr.ib(type=float, metadata={'sql': '{name} real'})
    battery = attr.ib(type=float, metadata={'sql': '{name} real'})
    id = attr.ib(type=int, default=None, metadata={'sql': '{name} integer primary key autoincrement'})

    @classmethod
    def additional_sql_fields(cls) -> List[str]:
        return super(Datapoint, cls).additional_sql_fields() + [
            'foreign key(sensor_id) references Sensor(id)',
            'foreign key(project_id) references Project(id)',
        ]

    @classmethod
    def get_all(
        cls,
        db_conn: SQLConnection,
        project_id: int = None,
        sensor_id: int = None,
    ) -> List['Datapoint']:
        if project_id is not None:
            data_cursor = db_conn.execute(
                """
                select id, project_id, sensor_id, angle, temperature, battery, timestamp
                from Datapoint
                where project_id = ?;
                """,
                (project_id,),
            )
        elif sensor_id is not None:
            data_cursor = db_conn.execute(
                """
                select id, project_id, sensor_id, angle, temperature, battery, timestamp
                from Datapoint
                where sensor_id = ?;
                """,
                (sensor_id,),
            )
        else:
            # Needs either a project or a sensor id.
            raise NotImplementedError()
        data_cursor.row_factory = cls.row_factory
        return data_cursor.fetchall()

    @classmethod
    def create_many(cls, conn: SQLConnection, datapoints: List['Datapoint']):
        conn.executemany(
            """
            insert into Datapoint (sensor_id, project_id, timestamp, angle, temperature, battery)
            values (?, ?, datetime(?), ?, ?, ?);
            """,
            (
                (d.sensor_id, d.project_id, d.timestamp, d.angle, d.temperature, d.battery)
                for d in datapoints
            ),
        )

    @classmethod
    def create(cls, db_conn: SQLConnection, **kwargs) -> 'Datapoint':
        raise RuntimeError('Use create_many() instead.')

    @classmethod
    def find(cls, db_conn: SQLConnection, datapoint_id: int = Required) -> Optional['Datapoint']:
        if datapoint_id is None:
            raise ValueError('datapoint_id is required')

        cursor = db_conn.execute(
            """
            select id, project_id, sensor_id, angle, temperature, battery, timestamp
            from Datapoint
            where id = ?;
            """,
            (datapoint_id,),
        )
        cursor.row_factory = cls.row_factory
        return cursor.fetchone()

    @classmethod
    def format_timestamp(cls, timestamp: datetime = None) -> str:
        if timestamp:
            return timestamp.isoformat()
        return 'no data'

    @classmethod
    def format_temperature(cls, temperature: float) -> str:
        return f'{temperature:2.1f}'

    @classmethod
    def format_gravity(cls, gravity: float) -> str:
        return f'{gravity:1.3f}'

    @classmethod
    def format_battery(cls, battery: float) -> str:
        return f'{battery:2.2f}'

    @classmethod
    def format_angle(cls, angle: float) -> str:
        return f'{angle:3.1f}'

    def edit(self, db_conn: SQLConnection, **kwargs):
        raise RuntimeError('Should not be used.')

    def delete(self, db_conn: SQLConnection):
        db_conn.execute(
            """
            delete from Datapoint where id=?;
            """,
            (self.id,),
        )

    def timestamp_as_str(self) -> str:
        return self.format_timestamp(self.timestamp)

    def temperature_as_str(self):
        return self.format_temperature(self.temperature)

    def gravity_as_str(self):
        return self.format_gravity(self.gravity)

    def battery_as_str(self):
        # TODO(tr) Use calibration to know that.
        return self.format_battery(self.battery)

    def angle_as_str(self):
        return self.format_angle(self.angle)

    @property
    def gravity(self):
        # TODO(tr) Use an actual algorithm with the sensor's config to convert
        # Transforms 45 to 1.045
        return 1.0 + self.angle / 1000

    def as_datatable(self):
        return {
            'when': {
                'label': self.timestamp_as_str(),
                'timestamp': self.timestamp.timestamp(),
            },
            'gravity': self.gravity_as_str(),
            'angle': self.angle_as_str(),
            'temperature': self.temperature_as_str(),
            'battery': self.battery_as_str(),
        }
