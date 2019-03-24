# brew-monitor Front End
Web interface for the brew-monitor

**This project is under development and not ready for the public.**

# Setup

This project is using [http://flask.pocoo.org/](Flask) with _python3_.

Use the provided _requirements.txt_ file to setup your python environment.

# Runing a debug setup

Start the flask debug server:
```
$> python3 python/run_server
```

By default it will run on [http://localhost:5000/]()

## Webserver view

Deploy flask using your favourite means - see [http://flask.pocoo.org/docs/1.0/quickstart/#deploying-to-a-web-server](Flask docs)

Just direct your browser to the root of the flask server. E.g. [http://localhost:5000/]()

## Storage API

The server should provide a _/storage/sensor/add_data_ path that expects the data as JSON.

### Parameters

Currently the API is expecting only 1 entry per call with the following fields:

* _sensor_id_: the sensor ID in the DB, as a string.
* _gravity_: as a floating point number encoded in a string.
* _temperature_: as a floating point number encoded in a string. The unit is expected to be Celcius.

### Response

The API will search the DB for the provided sensor ID and find the matching project.

* _created_: list of objects that have the attributes:
    * all of the parameters listed above, and:
    * _project_id_: the project ID that was found, as a sting. If the project was not found will return _null_.
    * _timestamp_: when was the recording stored, as an integer. This is in seconds since Epoch.

### E.g. of usage

```
$> curl \
  -H "Content-Type: application/json" \
  http://localhost:5000/storage/sensor/add_data \
  -d '{"sensor_id": "s123456", "gravity": "1.015", "temperature": "20.5"}'

{"created": [{"sensor_id": "s123456", "project_id": "p123456", "timestamp": 1554034368, "gravity": "1.015", "temperature": "20.5"}]}
```
