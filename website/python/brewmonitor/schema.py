from typing import Type

from brewmonitor.configuration import Configuration
from brewmonitor.storage.access import Sensor, Project, Datapoint, BaseTable
from brewmonitor.user import User


tables = (
    User,
    Sensor,
    Project,
    Datapoint,
)


def initialise_db(config: Configuration):

    if config.sqlite_file:
        print(f'Using SQL lite {config.sqlite_file}')
        open(config.sqlite_file, 'a+').close()  # Ensure the file exists

    with config.db_connection() as conn:
        for Table in tables:  # type: Type[BaseTable]
            r = Table.create_table_req()
            print(f'Creating table {Table.__name__}...')
            conn.execute(r)

        conn.commit()
