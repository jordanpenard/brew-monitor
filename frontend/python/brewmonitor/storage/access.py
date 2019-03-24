from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import attr


def timestamp_as_str(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


@attr.s
class Sensor:
    id = attr.ib(type=str)
    name = attr.ib(type=str)
    last_active = attr.ib(type=int, default=None)  # in SQL we would get that from the datapoints

    def last_active_str(self):
        if self.last_active is not None:
            return timestamp_as_str(self.last_active)
        return 'inactive'


@attr.s
class Project:
    id = attr.ib(type=str)
    name = attr.ib(type=str)
    sensor_ids = attr.ib(default=attr.Factory(list))  # Assuming 1 sensor per project but could change the sensor.


@attr.s
class DataPoints:
    sensor_id = attr.ib(type=str)
    project_id = attr.ib(type=str)
    timestamp = attr.ib(type=int)
    gravity = attr.ib(type=float)
    temperature = attr.ib(type=float)


@attr.s
class ProjectData(Project):
    sensors = attr.ib(default=attr.Factory(dict))  # type: Dict[str, Sensor]
    data_points = attr.ib(default=attr.Factory(list))  # type: List[DataPoints]


@attr.s
class SensorData(Sensor):
    projects = attr.ib(default=attr.Factory(dict))  # type: Dict[str, Project]
    data_points = attr.ib(default=attr.Factory(list))  # type: List[DataPoints]


def _past(n_min) -> int:
    return int((datetime.now() - timedelta(minutes=5 * n_min)).timestamp())


_fake_sensors = [
    Sensor('s123456', 'green sensor', _past(1)),
    Sensor('s123455', 'brown sensor', _past(1)),
]
_fake_projects = [
    Project('p123456', 'Brown Ale #12', ['s123456']),
    Project('p654321', 'Super IPA', ['s123456', 's123455'])
]
_fake_datapoints = [
    DataPoints('s123455', 'p123450', _past(10), 1.020, 25.0),  # Missing sensor data
    DataPoints('s123456', 'p123456', _past(8), 1.020, 25.0),
    DataPoints('s123456', 'p123456', _past(7), 1.018, 24.0),
    DataPoints('s123456', 'p123456', _past(6), 1.016, 24.0),
    DataPoints('s123456', 'p123456', _past(5), 1.014, 25.0),
    DataPoints('s123456', 'p123456', _past(4), 1.012, 23.0),
    DataPoints('s123456', 'p123456', _past(3), 1.010, 20.0),
    DataPoints('s123456', 'p123456', _past(2), 1.008, 21.0),
    DataPoints('s123456', 'p123456', _past(1), 1.006, 22.0),

    DataPoints('s123456', 'p654321', _past(10), 1.030, 15.0),
    DataPoints('s123456', 'p654321', _past(8), 1.030, 15.0),
    DataPoints('s123456', 'p654321', _past(7), 1.028, 14.0),
    DataPoints('s123456', 'p654321', _past(6), 1.026, 14.0),
    DataPoints('s123456', 'p654321', _past(5), 1.024, 15.0),
    DataPoints('s123456', 'p654321', _past(4), 1.022, 13.0),
    DataPoints('s123456', 'p654321', _past(3), 1.020, 10.0),
    DataPoints('s123456', 'p654321', _past(2), 1.018, 11.0),
    DataPoints('s123456', 'p654321', _past(1), 1.016, 12.0),

    DataPoints('s123455', 'p654321', _past(210), 1.030, 15.0),
    DataPoints('s123455', 'p654321', _past(208), 1.030, 15.0),
    DataPoints('s123455', 'p654321', _past(207), 1.028, 14.0),
    DataPoints('s123455', 'p654321', _past(206), 1.026, 14.0),
    DataPoints('s123455', 'p654321', _past(205), 1.024, 15.0),
    DataPoints('s123455', 'p654321', _past(204), 1.022, 13.0),
    DataPoints('s123455', 'p654321', _past(203), 1.020, 10.0),
    DataPoints('s123455', 'p654321', _past(202), 1.018, 11.0),
    DataPoints('s123455', 'p654321', _past(201), 1.016, 12.0),

    DataPoints('s123455', 'p654310', _past(201), 1.016, 12.0),  # Missing project data
]


def get_projects():
    return _fake_projects


def get_active_project_for_sensor(sensor_id):
    # type: (str) -> Tuple[Optional[Sensor], Optional[Project]]

    for sens in _fake_sensors:
        if sens.id == sensor_id:
            sensor = sens
            break
    else:
        sensor = None

    if sensor is not None:
        for proj in _fake_projects:
            if proj.sensor_ids and proj.sensor_ids[0] == sensor_id:
                project = proj
                break
        else:
            project = None
    else:
        project = None

    return sensor, project


def insert_datapoints(datapoints):
    # type: (DataPoints) -> None
    _fake_datapoints.append(datapoints)

    for sens in _fake_sensors:
        sens.last_active = datapoints.timestamp


def get_project_data(project_id):
    # type: (str) -> Optional[ProjectData]
    for proj in _fake_projects:
        if proj.id == project_id:
            sensors = {
                sens.id: sens
                for sens in _fake_sensors if sens.id in proj.sensor_ids
            }
            project = ProjectData(id=proj.id, name=proj.name, sensor_ids=proj.sensor_ids, sensors=sensors)
            break
    else:
        return  # Did not find project

    for dat in _fake_datapoints:
        if dat.project_id == project.id:
            project.data_points.append(dat)
            if dat.sensor_id not in project.sensors:
                project.sensors[dat.sensor_id] = Sensor(dat.sensor_id, '')

    return project


def get_sensor_data(sensor_id):
    # type: (str) -> Optional[SensorData]
    for sens in _fake_sensors:
        if sens.id == sensor_id:
            sensor = SensorData(id=sens.id, name=sens.name)
            break
    else:
        return  # Not found

    projects = {}
    for dat in _fake_datapoints:
        if dat.sensor_id == sensor.id:
            sensor.data_points.append(dat)
            # Not unique, apparently...
            if dat.project_id not in projects:
                for proj in _fake_projects:
                    if sensor.id in proj.sensor_ids:
                        projects[dat.project_id] = proj
                        break
                else:
                    projects[dat.project_id] = Project(dat.project_id, '')

    sensor.projects = projects
    return sensor