# Brew Monitor

Web app for brewing beer. It monitors beer fermentation, allow building and storing recipes, track brew-day and track stock of ingedients. 
The sensor to track fermentation has it's own project here : https://github.com/jordanpenard/brew-monitor-sensor

## Deployment
The following needs to be setup while deploying the container :
- Port mapping for `TCP:80`

```
docker build -t brew-monitor .
docker run -dit --name brew-monitor --mount type=bind,source=`pwd`,target=/var/www/html -p 8000:80 --restart=always brew-monitor
```

Once a container is freshly deployed, there's a few things that needs setting up for the first time from inside the container (connect to it with `docker exec -it brew-monitor /bin/bash`)
```
cd /var/www/html
echo "SECRET_KEY = '$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')'" > core/secret.py
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
chown -R www-data:www-data /var/www/html
```

You will also need to change `CSRF_TRUSTED_ORIGINS` inside `core/settings.py` to match your public url in order to avoid a `CSRF verification failed` error.

## Updates
When you want to update to a new version, only the following should be required, and a backup of the database is recommended
```
cd /var/www/html
cp db.sqlite3 db.sqlite3.bak
sudo -u www-data git pull
sudo -u www-data python3 manage.py migrate
```
Then restart your container.

## Storage API

This is how the fermentation sensor sends data back to the Brew monitor.
The server should provide a `/storage/sensor/add_data` path that expects the data as JSON.

### Parameters

The API is expecting only 1 entry per call with the following fields:

* `sensor_id`: the sensor ID in the DB, as an integer.
* `angle`: as a floating point number encoded in a string, in degrees. The calibration process will allow to compute a gravity measure.
* `temperature`: as a floating point number encoded in a string. The unit is expected to be Celsius.
* `battery`: as an floating point number encoded in a string. The unit is expected to be Volt, the calibration process will allow to compute a battery percentage.

### Response

The API will search the DB for the provided sensor ID and find the matching project.

* `created`: list of objects that have the attributes:
    * all the parameters listed above, and:
    * `project_id`: the project ID that was found, as an integer. If the project was not found will return _null_.
    * `timestamp`: when was the recording stored, as an integer. This is in seconds since Epoch.

### E.g. of usage

```
$> curl \
  -H "Content-Type: application/json" \
  http://localhost:8000/storage/sensor/add_data \
  -d '{"sensor_id": 1, "angle": "14.3", "temperature": "20.3", "battery": "2.6", "secret": "secret"}'

{"created": [{"sensor_id": 1, "project_id": 1, "timestamp": 1554034368, "angle": "15.5", "temperature": "20.5", "battery": 2800}]}
```

## TODO

- [ ] set calibration data
- [ ] workout how to compute _gravity_ from _angle_
