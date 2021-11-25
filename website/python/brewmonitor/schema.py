from typing import Type

from brewmonitor.configuration import Configuration
from brewmonitor.storage.tables import BaseTable, Sensor, Project, Datapoint, User


tables = (
    User,
    Sensor,
    Project,
    Datapoint,
)


def initialise_db(config: Configuration):

    if config.sqlite_file:
        open(config.sqlite_file, 'a+').close()  # Ensure the file exists

    with config.db_connection() as conn:
        for Table in tables:  # type: Type[BaseTable]
            r = Table.create_table_req()
            conn.execute(r)

        conn.commit()
