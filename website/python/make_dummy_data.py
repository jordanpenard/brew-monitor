import os
from datetime import datetime, timedelta

from brewmonitor.configuration import Configuration
from brewmonitor.schema import initialise_db
from brewmonitor.storage.access import Sensor, Project, Datapoint
from brewmonitor.user import User


def _past(n_min) -> datetime:
    return datetime.now() - timedelta(minutes=5 * n_min)


def make_dummy_data(config: Configuration, admin_pwd: str):
    initialise_db(config)

    with config.db_connection() as conn:
        print('Creating content...')

        u1 = User.create(conn, 'toto', admin_pwd, True)
        u2 = User.create(conn, 'titi', 'pass', False)

        green = Sensor.create(conn, 'green sensor', 'secret', u1)
        brown = Sensor.create(conn, 'brown sensor', 'secret', u2)
        sad_sensor = Sensor.create(conn, 'sad sensor', 'secret', u1)

        # Set a min and max battery only for 2 sensors
        conn.execute(
            '''
                update Sensor set min_battery=1, max_battery=10
                where id!=?
            ''',
            (sad_sensor.id,)
        )
        #
        # conn.execute(
        #     '''
        #     insert into Sensor (name, secret, owner, min_battery, max_battery)
        #     values
        #     ('green sensor', 'secret', 1, 1, 10),
        #     ('brown sensor', 'secret', 1, 2, 20),
        #     ('sad sensor', 'secret', 1, null, null)
        #     ;
        #     '''
        # )

        ale = Project.create(conn, 'Brown Ale #12', u1.id)
        ipa = Project.create(conn, 'Super IPA', u1.id)
        _ = Project.create(conn, 'Sad project', u1.id)

        ale.attach_sensor(conn, green.id)
        ipa.attach_sensor(conn, brown.id)

        # conn.execute(
        #     '''
        #     insert into Project (name, active_sensor, owner)
        #     values ('Brown Ale #12', 1, 1), ('Super IPA', 2, 1), ('Sad project', null, 1);
        #     '''
        # )

        data_points = [
            Datapoint(green.id, ale.id, _past(24 * 3600 + 60), 20, 25.0, 10.0),
            Datapoint(green.id, ale.id, _past(24 * 3600 + 55), 18, 24.0, 9.8),
            Datapoint(green.id, ale.id, _past(24 * 3600 + 50), 16, 23.5, 9.8),
            Datapoint(green.id, ale.id, _past(24 * 3600 + 45), 14, 23.0, 9.7),
            # Missing 40
            Datapoint(green.id, ale.id, _past(24 * 3600 + 35), 10, 22.0, 9.6),
            Datapoint(green.id, ale.id, _past(24 * 3600 + 30), 8, 21.0, 9.5),
            Datapoint(green.id, ale.id, _past(24 * 3600 + 25), 6, 20.0, 9.4),

            # As if sensor 2 wasn't configured properly at first
            Datapoint(brown.id, None, _past(120), 40, 25.0, 7.5),
            Datapoint(brown.id, None, _past(115), 35, 24.0, 7.4),
            Datapoint(brown.id, None, _past(110), 30, 23.5, 7.3),
            Datapoint(brown.id, None, _past(105), 25, 23.0, 7.2),
            Datapoint(brown.id, None, _past(100), 20, 23.0, 7.1),
            Datapoint(brown.id, None, _past(95), 15, 22.0, 7.0),
            Datapoint(brown.id, None, _past(90), 10, 21.0, 6.9),
            Datapoint(brown.id, None, _past(85), 5, 20.0, 6.8),

            Datapoint(brown.id, ipa.id, _past(60), 40, 25.0, 3.0),
            Datapoint(brown.id, ipa.id, _past(55), 35, 24.0, 3.5),
            Datapoint(brown.id, ipa.id, _past(50), 30, 23.5, 3.4),
            Datapoint(brown.id, ipa.id, _past(45), 25, 23.0, 3.3),
            Datapoint(brown.id, ipa.id, _past(40), 20, 23.0, 3.2),
            Datapoint(brown.id, ipa.id, _past(35), 15, 22.0, 3.1),
            Datapoint(brown.id, ipa.id, _past(30), 10, 21.0, 3.0),
            Datapoint(brown.id, ipa.id, _past(25), 5, 20.0, 2.9),
        ]
        Datapoint.create_many(conn, data_points)
        # conn.executemany(
        #     '''
        #     insert into Datapoint (sensor_id, project_id, timestamp, angle, temperature, battery)
        #     values (?, ?, datetime(?), ?, ?, ?);
        #     ''',
        #     data_points
        # )


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--admin-password', type=str, default='admin')
    parser.add_argument('--clear', action='store_true', help='First clear the data')

    args = parser.parse_args()

    cfg_file = os.environ.get('BREWMONITOR_CONFIG', './debug_config.yaml')
    cfg = Configuration.load(cfg_file)

    if args.clear:
        print(f'Clearing content from {cfg.sqlite_file}')
        open(cfg.sqlite_file, 'w').close()

    make_dummy_data(cfg, args.admin_password)
