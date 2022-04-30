from typing import Dict, List, Optional, AnyStr, Tuple

import attr
from flask import current_app

from brewmonitor.configuration import SQLConnection, config


from brewmonitor.storage.tables import Sensor, Project, Datapoint, User


@attr.s
class ProjectData(Project):
    sensors = attr.ib(type=dict, default=attr.Factory(dict))  # type: Dict[int, Sensor]
    data_points = attr.ib(type=list, default=attr.Factory(list))  # type: List[Datapoint]

    @classmethod
    def get_data(cls, db_conn: SQLConnection, project_id: int) -> Optional["ProjectData"]:
        project_data = cls.find(db_conn, project_id=project_id)
        if not project_data:
            return

        sensor_ids = set()
        for row in Datapoint.get_all(db_conn, project_id):
            project_data.data_points.append(row)
            sensor_ids.add(row.sensor_id)

        # TODO(tr) do a sensor_id in []
        # TODO(tr) ensure the active sensor is first?
        current_app.logger.debug(f'All sensors are: {str(sensor_ids)}')
        for s_id in sensor_ids:
            sensor = Sensor.find(db_conn, s_id)
            if sensor is not None:
                project_data.sensors[s_id] = sensor
                current_app.logger.debug(f'Found sensor_id={s_id}({type(s_id)}) is {str(sensor)}')
            else:
                current_app.logger.debug(f'Unknown sensor_id={s_id}')

        return project_data


@attr.s
class SensorData(Sensor):
    projects = attr.ib(type=dict, factory=dict)  # type: Dict[int, Project]
    data_points = attr.ib(type=list, factory=list)  # type: List[Datapoint]

    @classmethod
    def get_data(cls, db_conn: SQLConnection, sensor_id: int) -> Optional["SensorData"]:
        sensor_data = cls.find(db_conn, sensor_id)
        if not sensor_data:
            return

        project_ids = set()
        for row in Datapoint.get_all(db_conn, sensor_id=sensor_id):
            sensor_data.data_points.append(row)
            if row.project_id is not None:
                project_ids.add(row.project_id)

        # TODO(tr) Do a proper select id in []
        for p_id in project_ids:
            project = Project.find(db_conn, project_id=p_id)
            if project is not None:
                sensor_data.projects[p_id] = project

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


def edit_sensor(sensor: Sensor, name: str, secret: str, owner: User, max_battery: int, min_battery: int):
    with config().db_connection() as db_conn:
        return sensor.edit(
            db_conn,
            name=name,
            secret=secret,
            owner=owner,
            max_battery=float(max_battery),
            min_battery=float(min_battery),
        )


def remove_sensor(sensor: Sensor):
    with config().db_connection() as db_conn:
        return sensor.delete(db_conn)


def get_active_project_for_sensor(sensor_id: int) -> Tuple[Optional[Sensor], Optional[Project]]:
    with config().db_connection() as db_conn:
        return Sensor.find(db_conn, sensor_id), ProjectData.by_active_sensor(db_conn, sensor_id)


def insert_datapoints(datapoints: List[Datapoint]):
    with config().db_connection() as db_conn:
        Datapoint.create_many(db_conn, datapoints)


def edit_project(project: Project, name: str, owner: User):
    with config().db_connection() as db_conn:
        project.edit(db_conn, name, owner)


def remove_project(project: Project):
    with config().db_connection() as db_conn:
        return project.delete(db_conn)


def get_project_data(project_id: int) -> Optional[ProjectData]:
    with config().db_connection() as db_conn:
        return ProjectData.get_data(db_conn, project_id)


def get_sensor_data(sensor_id: int) -> Optional[SensorData]:
    with config().db_connection() as db_conn:
        return SensorData.get_data(db_conn, sensor_id)


def insert_project(name: AnyStr, owner: User) -> Project:
    with config().db_connection() as db_conn:
        return Project.create(db_conn, name, owner)


def insert_sensor(name: AnyStr, secret: AnyStr, owner: User) -> Sensor:
    with config().db_connection() as db_conn:
        return Sensor.create(db_conn, name, secret, owner)


def update_project_sensor(project: Project, sensor_id: Optional[int] = None) -> None:
    with config().db_connection() as db_conn:
        project.attach_sensor(db_conn, sensor_id)


def get_datapoint(datapoint_id: int) -> Optional[Datapoint]:
    with config().db_connection() as db_conn:
        return Datapoint.find(db_conn, datapoint_id=datapoint_id)


def remove_datapoint(datapoint: Datapoint):
    with config().db_connection() as db_conn:
        datapoint.delete(db_conn)


def get_users() -> List[User]:
    with config().db_connection() as db_conn:
        return User.get_all(db_conn)


def get_user(user_id: int) -> Optional[User]:
    with config().db_connection() as db_conn:
        return User.find(db_conn, user_id)


def insert_user(username: str, password: str, is_admin: bool) -> User:
    with config().db_connection() as db_conn:
        return User.create(db_conn, username, password, is_admin)


def remove_user(user: User):
    with config().db_connection() as db_conn:
        return user.delete(db_conn)
