from datetime import datetime, timedelta

import pytest

from brewmonitor.storage.tables import Sensor, Project, Datapoint, User, BaseTable
from test_brewmonitor.conftest import config_from_client, preset_when


class TestCoverage:
    # additional bits to trick the coverage

    def test_base_class_raises_not_implemented(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            for cls_method in ('get_all', 'find', 'create'):
                with pytest.raises(NotImplementedError):
                    getattr(BaseTable, cls_method)(conn)

            base_obj = super(User, User.create(conn, username='user', password='pass', is_admin=True))
            for method in ('edit', 'delete'):
                with pytest.raises(NotImplementedError):
                    getattr(base_obj, method)(conn)


class TestUser:

    def test_get_all(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            users = User.get_all(conn)

        assert len(users) == 2

        assert users[0] == User(
            id=1,
            username='toto',
            is_admin=True,
        )
        assert users[1] == User(
            id=2,
            username='titi',
            is_admin=False
        )

    def test_get_all_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            with pytest.raises(ValueError):
                User.get_all(conn, user_id=1)

    def test_find_by_user_id(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert User.find(conn, user_id=1) == User(
                id=1,
                username='toto',
                is_admin=True,
            )

    def test_find_nothing(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            assert User.find(conn, user_id=1234) is None

    def test_find_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            with pytest.raises(ValueError):
                User.find(conn)

    def test_create(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            user = User.create(conn, username='toto', password='pass', is_admin=False)
            # check object was created correctly, no password in the object!
            assert user.username == 'toto'
            assert not user.is_admin
            assert user.id == 1
            assert not hasattr(user, 'password')

        with bm_config.db_connection() as conn:
            db_user = User.find(conn, user_id=1)
            assert db_user.username == 'toto'
            assert not db_user.is_admin
            assert db_user.id == 1
            assert not hasattr(db_user, 'password')

    @pytest.mark.parametrize('remove_arg', (
        'username',
        'password',
        'is_admin',
    ))
    def test_create_missing_args(self, tmp_app, remove_arg):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            kwargs = {
                'username': 'toto',
                'password': 'pass',
                'is_admin': True,
            }
            kwargs.pop(remove_arg)
            with pytest.raises(ValueError):
                User.create(conn, **kwargs)

    def test_verify(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert User.verify(conn, username='toto', password='admin') == User(
                id=1,
                username='toto',
                is_admin=True,
            )

    def test_verify_fails(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert User.verify(conn, username='toto', password='wrong') is None

    def test_edit_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            user = User.create(conn, username='toto', password='pass', is_admin=False)
            with pytest.raises(RuntimeError):
                user.edit(conn, password='new pass', is_admin=False)

    def test_delete_detached_user(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            user = User.create(conn, username='toto', password='pass', is_admin=False)

        with bm_config.db_connection() as conn:
            user.delete(conn)

        with bm_config.db_connection() as conn:
            assert User.find(conn, user_id=user.id) is None

    def test_delete(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            user = User.create(conn, username='toto', password='pass', is_admin=False)
            project = Project.create(conn, name='project', owner=user)
            sensor = Sensor.create(conn, name='sensor', secret='secret', owner=user)

        with bm_config.db_connection() as conn:
            user.delete(conn)

        with bm_config.db_connection() as conn:
            assert User.find(conn, user_id=user.id) is None
            assert Project.find(conn, project_id=project.id).owner is None, 'should not have been affected'
            assert Sensor.find(conn, sensor_id=sensor.id).owner is None, 'should not have been affected'


class TestSensor:

    def test_get_all(self, preset_app):
        bm_config = config_from_client(preset_app)

        sensors = Sensor.get_all(bm_config.db_connection())

        assert len(sensors) == 3, sensors

        by_name = {}
        by_owner = {}

        for s in sensors:
            by_name[s.name] = s
            if s.owner not in by_owner:
                by_owner[s.owner] = []
            by_owner[s.owner].append(s)

        assert sorted(by_name.keys()) == ['brown sensor', 'green sensor', 'sad sensor']
        assert len(by_owner['toto']) == 2
        assert len(by_owner['titi']) == 1

    def test_find(self, preset_app):
        bm_config = config_from_client(preset_app)

        expected = Sensor(
            id=1,
            name='green sensor',
            secret='secret',
            owner='toto',
            max_battery=10.0,
            min_battery=1.0,
            # see preset_client when
            last_active=datetime(2021, 11, 26, 11, 34) - timedelta(days=1, minutes=25),
            last_battery=9.4,
            linked_project=1,  # ale
        )

        assert Sensor.find(bm_config.db_connection(), expected.id) == expected

    def test_find_nothing(self, preset_app):
        bm_config = config_from_client(preset_app)

        assert Sensor.find(bm_config.db_connection(), 1234) is None

    def test_find_invalid(self, preset_app):
        bm_config = config_from_client(preset_app)

        with pytest.raises(ValueError):
            Sensor.find(bm_config.db_connection())

    def test_create_sensor(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, 'toto', 'admin', True)
            new_sensor = Sensor.create(conn, 'new sensor fun', 'new secret', owner)

            assert new_sensor.name == 'new sensor fun'
            assert new_sensor.secret == 'new secret'
            assert new_sensor.owner == 'toto'
            # Default value
            assert new_sensor.max_battery == 4.0
            assert new_sensor.min_battery == 2.0
            # Not filled at creation
            assert new_sensor.linked_project is None
            # available from Datapoints, so should have nothing yet
            assert new_sensor.last_active is None
            assert new_sensor.last_battery is None

            Datapoint.create_many(
                conn,
                [
                    Datapoint(new_sensor.id, None, datetime(2021, 11, 26, 12, 40), 23, 20.0, 9.5),
                    Datapoint(new_sensor.id, None, datetime(2021, 11, 26, 12, 45), 23.3, 19.4, 9.2),
                ]
            )

        # now that we have data points we should be able to find the sensor
        updated_sensor = Sensor.find(bm_config.db_connection(), new_sensor.id)

        assert updated_sensor.name == 'new sensor fun'
        assert updated_sensor.secret == 'new secret'
        assert updated_sensor.owner == 'toto'
        # Default value
        assert updated_sensor.max_battery == 4.0
        assert updated_sensor.min_battery == 2.0
        # after creating datapoints
        assert updated_sensor.last_active == datetime(2021, 11, 26, 12, 45)
        assert updated_sensor.last_battery == 9.2

        # No need to delete the sensor and user because tmp_client is destroyed

    @pytest.mark.parametrize('remove_arg', (
        'name',
        'secret',
        'owner',
    ))
    def test_create_sensor_invalid(self, tmp_app, remove_arg):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, 'toto', 'admin', True)
            kwargs = {
                'name': 'new sensor fun',
                'secret': 'new secret',
                'owner': owner,
            }
            kwargs.pop(remove_arg)
            with pytest.raises(ValueError):
                Sensor.create(conn, **kwargs)

    def test_edit_all_attributes(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, 'toto', 'admin', True)
            next_owner = User.create(conn, 'sasa', 'pass', False)
            new_sensor = Sensor.create(conn, 'new sensor fun', 'new secret', owner)

        assert new_sensor.name == 'new sensor fun'
        assert new_sensor.secret == 'new secret'
        assert new_sensor.owner == 'toto'
        # Default value
        assert new_sensor.max_battery == 4.0
        assert new_sensor.min_battery == 2.0

        with bm_config.db_connection() as conn:
            new_sensor.edit(
                conn,
                name='new sensor',
                secret='another secret',
                owner=next_owner,
                max_battery=10.0,
                min_battery=1.0,
            )
            # Check that the object was updated
            assert new_sensor.name == 'new sensor'
            assert new_sensor.secret == 'another secret'
            assert new_sensor.owner == 'sasa'
            assert new_sensor.max_battery == 10.0
            assert new_sensor.min_battery == 1.0

        with bm_config.db_connection() as conn:
            db_sensor = Sensor.find(conn, sensor_id=new_sensor.id)
            # check that the db was updated
            assert db_sensor.name == 'new sensor'
            assert db_sensor.secret == 'another secret'
            assert db_sensor.owner == 'sasa'
            assert db_sensor.max_battery == 10.0
            assert db_sensor.min_battery == 1.0

    def test_edit_unknown_attributes_is_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, 'toto', 'admin', True)
            new_sensor = Sensor.create(conn, 'new sensor fun', 'new secret', owner)

        with pytest.raises(ValueError):
            new_sensor.edit(
                bm_config.db_connection(),
                name='new sensor',
                unknown_param=1,
            )

    def test_cascade_delete(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, 'toto', 'admin', True)
            new_sensor = Sensor.create(conn, 'new sensor fun', 'new secret', owner)
            other_sensor = Sensor.create(conn, 'other sensor', 'other secret', owner)
            attached_project = Project.create(conn, 'new project', owner)
            attached_project.attach_sensor(conn, new_sensor.id)
            Datapoint.create_many(conn, [
                Datapoint(new_sensor.id, attached_project.id, datetime(2021, 11, 30, 11, 23), 34, 18, 5.4, 1),
                Datapoint(new_sensor.id, None, datetime(2021, 11, 30, 11, 24), 34, 18, 5.4, 2),
                Datapoint(other_sensor.id, attached_project.id, datetime(2021, 11, 30, 11, 23), 34, 18, 5.4, 3),
            ])

        with bm_config.db_connection() as conn:
            assert Project.find(conn, project_id=attached_project.id).active_sensor == new_sensor.id
            assert Datapoint.find(conn, datapoint_id=1).sensor_id == new_sensor.id
            assert Datapoint.find(conn, datapoint_id=2).sensor_id == new_sensor.id
            assert Datapoint.find(conn, datapoint_id=3).sensor_id == other_sensor.id

            new_sensor.delete(conn)

        with bm_config.db_connection() as conn:
            assert Project.find(conn, project_id=attached_project.id).active_sensor is None, 'Should have been detached'
            assert Datapoint.find(conn, datapoint_id=1) is None, 'Should have been deleted'
            assert Datapoint.find(conn, datapoint_id=2) is None, 'Should have been deleted'
            assert Datapoint.find(conn, datapoint_id=3) is not None, 'Should have been unaffected'


class TestProject:

    def test_get_all(self, preset_app):
        bm_config = config_from_client(preset_app)

        projects = Project.get_all(bm_config.db_connection())

        assert len(projects) == 3, projects

        by_name = {}
        by_owner = {}

        for p in projects:
            by_name[p.name] = p
            if p.owner not in by_owner:
                by_owner[p.owner] = []
            by_owner[p.owner].append(p)

        assert sorted(by_name.keys()) == ['Brown Ale #12', 'Sad project', 'Super IPA']
        assert len(by_owner) == 1, 'Should not have other users than "toto"'
        assert len(by_owner['toto']) == 3

    def test_get_all_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            with pytest.raises(ValueError):
                Project.get_all(conn, project_id=1)

    def test_find(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert Project.find(conn, project_id=1) == Project(
                id=1,
                name='Brown Ale #12',
                owner='toto',
                active_sensor=1,  # green
                first_active=preset_when - timedelta(days=1, minutes=60),
                last_active=preset_when - timedelta(days=1, minutes=25),
                first_angle=20,
                last_angle=6,
                last_temperature=20.0,
            )

    def test_find_nothing(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert Project.find(conn, project_id=1234) is None

    def test_find_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            with pytest.raises(ValueError):
                Project.find(conn)

    def test_by_active_sensor(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert Project.by_active_sensor(conn, sensor_id=1) == Project(
                id=1,
                name='Brown Ale #12',
                owner='toto',
                active_sensor=1,  # green
                first_active=preset_when - timedelta(days=1, minutes=60),
                last_active=preset_when - timedelta(days=1, minutes=25),
                first_angle=20,
                last_angle=6,
                last_temperature=20.0,
            )

    def test_create(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            Project.create(
                conn,
                name='new project',
                owner=owner,
            )

    @pytest.mark.parametrize('remove_arg', (
        'name',
        'owner'
    ))
    def test_create_invalid(self, tmp_app, remove_arg):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            kwargs = {
                'name': 'new project',
                'owner': owner
            }
            kwargs.pop(remove_arg)
            with pytest.raises(ValueError):
                Project.create(conn, **kwargs)

    def test_delete_cascade(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            new_project = Project.create(conn, name='new project', owner=owner)
            new_sensor = Sensor.create(conn, name='green', secret='secret', owner=owner)
            other_sensor = Sensor.create(conn, name='brown', secret='secret', owner=owner)
            new_project.attach_sensor(conn, new_sensor.id)

            Datapoint.create_many(conn, [
                Datapoint(new_sensor.id, None, datetime(2021, 11, 30, 14, 28), 23, 18, 3.4, id=1),
                Datapoint(new_sensor.id, new_project.id, datetime(2021, 11, 30, 14, 28), 23, 18, 3.4, id=2),
                Datapoint(other_sensor.id, new_project.id, datetime(2021, 11, 30, 14, 28), 23, 18, 3.4, id=3),
            ])

        with bm_config.db_connection() as conn:
            assert Project.find(conn, project_id=new_project.id).active_sensor == new_sensor.id
            assert Datapoint.find(conn, datapoint_id=1).project_id is None
            assert Datapoint.find(conn, datapoint_id=2).project_id == new_project.id
            assert Datapoint.find(conn, datapoint_id=3).project_id == new_project.id

            new_project.delete(conn)

        with bm_config.db_connection() as conn:
            assert Sensor.find(conn, sensor_id=new_sensor.id) is not None, 'active sensor should not have been deleted'
            assert Datapoint.find(conn, datapoint_id=1) is not None, 'should not have been affected'
            assert Datapoint.find(conn, datapoint_id=2) is None, 'should have been deleted'
            assert Datapoint.find(conn, datapoint_id=3) is None, 'should have been deleted'

    def test_edit_all_attributes(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            new_owner = User.create(conn, username='robot', password='captcha', is_admin=False)
            new_project = Project.create(conn, name='new project', owner=owner)
            new_sensor = Sensor.create(conn, name='green', secret='secret', owner=owner)

            new_project.attach_sensor(conn, new_sensor.id)

        assert new_project.name == 'new project'
        assert new_project.owner == 'user'

        with bm_config.db_connection() as conn:
            new_project.edit(conn, name='IPA project', owner=new_owner)
            # check that the object was modified
            assert new_project.name == 'IPA project'
            assert new_project.owner == 'robot'

        with bm_config.db_connection() as conn:
            db_project = Project.find(conn, project_id=new_project.id)
            # ensure that db was modified
            assert db_project.name == 'IPA project'
            assert db_project.owner == 'robot'

    @pytest.mark.parametrize('remove_arg', (
        'name',
        'owner',
    ))
    def test_edit_invalid(self, tmp_app, remove_arg):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            new_owner = User.create(conn, username='robot', password='captcha', is_admin=False)
            new_project = Project.create(conn, name='new project', owner=owner)

            kwargs = {
                'name': 'new name',
                'owner': new_owner,
            }
            kwargs.pop(remove_arg)

            with pytest.raises(ValueError):
                new_project.edit(conn, **kwargs)

    def test_attach_sensor(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            new_project = Project.create(conn, name='new project', owner=owner)

            sensor_a = Sensor.create(conn, name='sensor a', secret='secret', owner=owner)
            sensor_b = Sensor.create(conn, name='sensor b', secret='secret', owner=owner)

            assert new_project.active_sensor is None, 'initially no sensor attached'

            new_project.attach_sensor(conn, sensor_a.id)
            # check object is updated
            assert new_project.active_sensor == sensor_a.id

        with bm_config.db_connection() as conn:
            db_project = Project.find(conn, project_id=new_project.id)
            assert db_project.active_sensor == sensor_a.id

            db_project.attach_sensor(conn, sensor_b.id)
            assert db_project.active_sensor == sensor_b.id

    def test_detach_sensor(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=False)
            new_project = Project.create(conn, name='new project', owner=owner)

            sensor_a = Sensor.create(conn, name='sensor a', secret='secret', owner=owner)
            new_project.attach_sensor(conn, sensor_a.id)

        with bm_config.db_connection() as conn:
            new_project.attach_sensor(conn, sensor_id=None)
            # check object is updated
            assert new_project.active_sensor is None

        with bm_config.db_connection() as conn:
            db_project = Project.find(conn, project_id=new_project.id)
            # check db was updated
            assert db_project.active_sensor is None


class TestDatapoint:

    def test_get_all_not_implemented_without_project_and_sensor(self, preset_app):
        bm_config = config_from_client(preset_app)

        with pytest.raises(NotImplementedError):
            Datapoint.get_all(bm_config.db_connection())

    def test_get_all_for_project(self, preset_app):
        bm_config = config_from_client(preset_app)

        datapoints = Datapoint.get_all(bm_config.db_connection(), project_id=1)  # brown ale

        assert len(datapoints) == 7

        by_sensor = {}

        for d in datapoints:
            if d.sensor_id not in by_sensor:
                by_sensor[d.sensor_id] = []
            by_sensor[d.sensor_id].append(d)

        assert len(by_sensor) == 1, 'Should not have any other sensors than "green"'
        assert len(by_sensor[1]) == 7

        assert datapoints[0] == Datapoint(
            sensor_id=1,
            project_id=1,
            timestamp=preset_when - timedelta(days=1, minutes=60),
            angle=20,
            temperature=25.0,
            battery=10.0,
            id=datapoints[0].id,  # we don't care about the id
        )

    def test_get_all_for_sensor(self, preset_app):
        bm_config = config_from_client(preset_app)

        datapoints = Datapoint.get_all(bm_config.db_connection(), sensor_id=2)  # brown sensor

        assert len(datapoints) == 16

        by_project = {}

        for d in datapoints:
            if d.project_id not in by_project:
                by_project[d.project_id] = []
            by_project[d.project_id].append(d)

        assert len(by_project) == 2
        assert len(by_project[None]) == 8
        assert len(by_project[2]) == 8, '"Super IPA" should have half of the data points'

        assert datapoints[4] == Datapoint(
            sensor_id=2,
            project_id=None,
            timestamp=preset_when - timedelta(minutes=100),
            angle=20,
            temperature=23.0,
            battery=7.1,
            id=datapoints[4].id,  # we don't care about the id
        )

    def test_create_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            with pytest.raises(RuntimeError):
                Datapoint.create(conn)

    def test_create_many(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=True)
            project = Project.create(conn, name='IPA', owner=owner)
            sensor = Sensor.create(conn, name='green', secret='secret', owner=owner)

            # the id is actually not used!
            datapoints = [
                Datapoint(sensor.id, None, datetime(2021, 11, 30, 15, 10), 13, 18, 3.4),  # id=1
                Datapoint(sensor.id, project.id, datetime(2021, 11, 30, 15, 15), 15, 20, 4.4, id=1234),  # real id=2
            ]
            Datapoint.create_many(conn, datapoints)

            assert datapoints[0].id is None, 'should not have been modified'
            assert datapoints[1].id == 1234, 'should not have been modified'

        with bm_config.db_connection() as conn:
            db_data = Datapoint.get_all(conn, sensor_id=sensor.id)

            assert len(db_data) == len(datapoints)

            assert db_data[0].timestamp == datapoints[0].timestamp
            assert db_data[1].timestamp == datapoints[1].timestamp

    def test_find(self, preset_app):
        bm_config = config_from_client(preset_app)

        with bm_config.db_connection() as conn:
            assert Datapoint.find(conn, datapoint_id=1) == Datapoint(
                sensor_id=1,
                project_id=1,
                timestamp=preset_when - timedelta(days=1, minutes=60),
                angle=20.0,
                temperature=25.0,
                battery=10.0,
                id=1,
            )

    def test_find_nothing(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            assert Datapoint.find(conn, datapoint_id=1234) is None

    def test_find_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            with pytest.raises(ValueError):
                Datapoint.find(conn)

    def test_edit_invalid(self, tmp_app):
        bm_config = config_from_client(tmp_app)

        with bm_config.db_connection() as conn:
            owner = User.create(conn, username='user', password='pass', is_admin=True)
            sensor = Sensor.create(conn, name='green', secret='secret', owner=owner)

            # the id is actually not used!
            datapoints = [
                Datapoint(sensor.id, None, datetime(2021, 11, 30, 15, 10), 13, 18, 3.4),  # id=1
            ]
            Datapoint.create_many(conn, datapoints)

        with bm_config.db_connection() as conn:
            with pytest.raises(RuntimeError):
                datapoints[0].edit(conn)
