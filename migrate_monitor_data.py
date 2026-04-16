import sqlite3
import os
import datetime
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from django.contrib.auth.models import User
from monitor.models import Sensor, Project, Datapoint

def migrate_monitor_data():
    old_db_path = "old-brew-monitor.sqlite3"
    
    if not os.path.exists(old_db_path):
        print(f"Old database not found at {old_db_path}")
        return

    conn_old = sqlite3.connect(old_db_path)
    cursor_old = conn_old.cursor()

    # Cache users from old DB to avoid repeated queries
    print("Caching users...")
    old_user_map = {} # old_id -> username
    cursor_old.execute("SELECT id, username FROM User")
    for uid, username in cursor_old.fetchall():
        old_user_map[uid] = username

    # Cache Django users
    django_user_cache = {}
    for user in User.objects.all():
        django_user_cache[user.username] = user

    def get_or_create_django_user(username):
        if username not in django_user_cache:
            user, created = User.objects.get_or_create(username=username, defaults={
                "password": "!",
                "is_active": False,
            })
            django_user_cache[username] = user
        return django_user_cache[username]

    with transaction.atomic():
        # Clear existing data to avoid duplicates if re-run
        Datapoint.objects.all().delete()
        Project.objects.all().delete()
        Sensor.objects.all().delete()

        # Migrate Sensors
        print("Migrating sensors...")
        old_sensor_map = {} # old_id -> new_sensor_object
        cursor_old.execute("SELECT id, name, secret, owner, max_battery, min_battery FROM Sensor")
        sensors_to_create = []
        old_sensor_data = cursor_old.fetchall()
        
        for old_id, name, secret, owner_id, max_battery, min_battery in old_sensor_data:
            username = old_user_map.get(owner_id)
            user = get_or_create_django_user(username)
            sensor = Sensor(
                name=name,
                secret=secret,
                owner=user,
                max_battery=max_battery,
                min_battery=min_battery
            )
            sensors_to_create.append((old_id, sensor))

        created_sensors = Sensor.objects.bulk_create([s for _, s in sensors_to_create])
        for (old_id, _), new_sensor in zip(sensors_to_create, created_sensors):
            old_sensor_map[old_id] = new_sensor

        # Migrate Projects
        print("Migrating projects...")
        old_project_map = {} # old_id -> new_project_object
        cursor_old.execute("SELECT id, name, owner, active_sensor FROM Project")
        projects_to_create = []
        old_project_data = cursor_old.fetchall()

        for old_id, name, owner_id, active_sensor_id in old_project_data:
            username = old_user_map.get(owner_id)
            user = get_or_create_django_user(username)
            active_sensor = old_sensor_map.get(active_sensor_id)
            
            project = Project(
                name=name,
                owner=user,
                active_sensor=active_sensor
            )
            projects_to_create.append((old_id, project))

        created_projects = Project.objects.bulk_create([p for _, p in projects_to_create])
        for (old_id, _), new_project in zip(projects_to_create, created_projects):
            old_project_map[old_id] = new_project

        # Migrate Datapoints
        print("Migrating datapoints...")
        cursor_old.execute("SELECT COUNT(*) FROM Datapoint")
        total_datapoints = cursor_old.fetchone()[0]
        print(f"Total datapoints to migrate: {total_datapoints}")

        cursor_old.execute("SELECT sensor_id, project_id, timestamp, angle, temperature, battery FROM Datapoint")
        
        batch_size = 5000
        datapoints_batch = []
        count = 0
        
        while True:
            rows = cursor_old.fetchmany(batch_size)
            if not rows:
                break
            
            for old_sensor_id, old_project_id, timestamp_str, angle, temperature, battery in rows:
                sensor = old_sensor_map.get(old_sensor_id)
                project = old_project_map.get(old_project_id)
                
                if not sensor:
                    continue

                try:
                    dt_object = datetime.datetime.fromisoformat(timestamp_str)
                except ValueError:
                    # Fallback if format is slightly different
                    dt_object = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

                datapoints_batch.append(Datapoint(
                    sensor=sensor,
                    project=project,
                    timestamp=dt_object,
                    angle=angle,
                    temperature=temperature,
                    battery=battery
                ))
            
            Datapoint.objects.bulk_create(datapoints_batch)
            datapoints_batch = []
            count += len(rows)
            print(f"Migrated {count}/{total_datapoints} datapoints ({(count/total_datapoints)*100:.1f}%)", end='\r')

    conn_old.close()
    print("\nMonitor data migration completed successfully!")

if __name__ == "__main__":
    migrate_monitor_data()
