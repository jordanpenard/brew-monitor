import os
from datetime import datetime, timedelta

from brewmonitor.schema import initialise_db
from brewmonitor.configuration import Configuration


def _past(n_min) -> datetime:
    return datetime.now() - timedelta(minutes=5 * n_min)


os.environ['BREWMONITOR_CONFIG'] = './debug_config.yaml'

config = Configuration.load(os.environ.get('BREWMONITOR_CONFIG', './debug_config.yaml'))

initialise_db(config)

with config.db_connection() as conn:

    conn.execute(
        '''
        insert into User (username, password, is_admin)
        values ('toto', 'pass', true), ('titi', 'pass', false);
        '''
    )
    conn.execute(
        '''
        insert into Sensor (name, secret, owner)
        values ('green sensor', 'secret', 1), ('brown sensor', 'secret', 1), ('sad sensor', 'secret', 1);
        '''
    )
    conn.execute(
        '''
        insert into Project (name, active_sensor, owner)
        values ('Brown Ale #12', 1, 1), ('Super IPA', 2, 1), ('Sad project', null, 1);
        '''
    )

    data_points = [
        (1, 1, _past(24 * 3600 + 60), 20, 25.0, 10.0),
        (1, 1, _past(24 * 3600 + 55), 18, 24.0, 9.8),
        (1, 1, _past(24 * 3600 + 50), 16, 23.5, 9.8),
        (1, 1, _past(24 * 3600 + 45), 14, 23.0, 9.7),
        # Missing 40
        (1, 1, _past(24 * 3600 + 35), 10, 22.0, 9.6),
        (1, 1, _past(24 * 3600 + 30), 8, 21.0, 9.5),
        (1, 1, _past(24 * 3600 + 25), 6, 20.0, 9.4),

        # As if sensor 2 wasn't configured properly at first
        (2, None, _past(120), 40, 25.0, 7.5),
        (2, None, _past(115), 35, 24.0, 7.4),
        (2, None, _past(110), 30, 23.5, 7.3),
        (2, None, _past(105), 25, 23.0, 7.2),
        (2, None, _past(100), 20, 23.0, 7.1),
        (2, None, _past(95), 15, 22.0, 7.0),
        (2, None, _past(90), 10, 21.0, 6.9),
        (2, None, _past(85), 5, 20.0, 6.8),

        (2, 2, _past(60), 40, 25.0, 3.0),
        (2, 2, _past(55), 35, 24.0, 3.5),
        (2, 2, _past(50), 30, 23.5, 3.4),
        (2, 2, _past(45), 25, 23.0, 3.3),
        (2, 2, _past(40), 20, 23.0, 3.2),
        (2, 2, _past(35), 15, 22.0, 3.1),
        (2, 2, _past(30), 10, 21.0, 3.0),
        (2, 2, _past(25), 5, 20.0, 2.9),
    ]
    conn.executemany(
        '''
        insert into Datapoint (sensor_id, project_id, timestamp, angle, temperature, battery)
        values (?, ?, datetime(?), ?, ?, ?);
        ''',
        data_points
    )
