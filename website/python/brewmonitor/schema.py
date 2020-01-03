from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from brewmonitor.configuration import Configuration


def initialise_db(config):
    # type: (Configuration) -> None

    if config.sqlite_file:
        open(config.sqlite_file, 'a+').close()  # Ensure the file exists

    with config.db_connection() as conn:
        conn.execute(
            '''
            create table if not exists User (
                id integer primary key autoincrement,
                is_admin bool,
                username text not null,
                password text not null
            );
            '''
        )

        conn.execute(
            '''
            create table if not exists Sensor (
                id integer primary key autoincrement,
                name text not null,
                secret text not null,
                owner integer not null,
                max_battery float,
                min_battery float,
                battery float,
                foreign key(owner) references User(id)
            );
            '''
        )
    
        conn.execute(
            '''
            create table if not exists Project (
                id integer primary key autoincrement,
                name text not null,
                active_sensor integer,
                owner integer not null,
                foreign key(owner) references User(id),
                foreign key(active_sensor) references Sensor(id)
            ); 
            '''
        )

        conn.execute(
            '''
            create table if not exists Datapoint (
                id integer primary key autoincrement,
                temperature real,
                angle real,
                battery float,
                timestamp integer not null,
                sensor_id integer not null,
                project_id integer,
                foreign key(sensor_id) references Sensor(id),
                foreign key(project_id) references Project(id)
            );
            '''
        )

        conn.commit()
