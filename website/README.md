# brew-monitor Front End
Web interface for the brew-monitor.

**This project is under development and not ready for the public.**

# Setup

This project is using:
 
- [http://flask.pocoo.org/](Flask)
- python **3.7**

Use the provided _requirements.txt_ file to setup your python environment.

# Running a debug setup

**From the _website_ folder**

Create a python virtual env with the required libraries :
```
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the scratch folder where the debug db will be stored and optionally create dummy data:
```
mkdir storage
python python/make_dummy_data.py
```

The location of the DB can be changed in _debug_config.yaml_.

Start the flask debug server (from the _website_ folder):
```
python python/run_server
```

By default it will run on [http://localhost:5000/]()

## Webserver view

Deploy flask using your favourite means - see [http://flask.pocoo.org/docs/1.0/quickstart/#deploying-to-a-web-server](Flask docs). 

Just direct your browser to the root of the flask server. E.g. [http://localhost:5000/]()

### E.g. using WSGI ###

We installed everything from git in _/usr/local/brewmonitor/_.

Note on wsgi: you will need the WSGI that is compatible with your apache version **AND** python version.

```
$> pip3 install mod_wsgi
(...)
$> # Get the example of configuration to put in apache:
$> mod_wsgi-express module-config
(...)
```

/usr/local/www/wsgi-bin/brewmonitor.wsgi:
```python
#!/usr/local/bin/python3.7

import os
os.environ['BREWMONITOR_CONFIG'] = '/etc/brewmonitor/config.yaml'

import sys
sys.path.append('/usr/local/brewmonitor/website/python')

from brewmonitor.app import make_app
application = make_app('secret_key_example')
```

/etc/brewmonitor/config.yaml:
```yaml
sqlite file: '/var/run/brewmonitor/debug_flask.db'
```

Sample of of apache config:
```
${insert the mod_wsgi-express result here}
<VirtualHost *:80>
        ServerName brewmonitor.domain
        ServerAdmin admin.domain
        WSGIDaemonProcess brewmonitor threads=2 display-name=wsgi:brewmonitor
        WSGIScriptAlias / /usr/local/www/wsgi-bin/brewmonitor.wsgi
        DocumentRoot "/usr/local/www/apache24/brew-monitor/website"
        <Directory /usr/local/www/apache24/brew-monitor/website/>
                Options FollowSymLinks Includes
                AllowOverride All
                Order allow,deny
                Allow from all
        </Directory>
</VirtualHost>
```


## Storage API

The server should provide a _/storage/sensor/add_data_ path that expects the data as JSON.

### Parameters

Currently the API is expecting only 1 entry per call with the following fields:

* _sensor_id_: the sensor ID in the DB, as an integer.
* _angle_: as a floating point number encoded in a string, in degrees. The calibration process will allow to compute a gravity measure.
* _temperature_: as a floating point number encoded in a string. The unit is expected to be Celsius.
* _battery_: as an floating point number encoded in a string. The unit is expected to be Volt, the calibration process will allow to compute a battery percentage.

### Response

The API will search the DB for the provided sensor ID and find the matching project.

* _created_: list of objects that have the attributes:
    * all of the parameters listed above, and:
    * _project_id_: the project ID that was found, as an integer. If the project was not found will return _null_.
    * _timestamp_: when was the recording stored, as an integer. This is in seconds since Epoch.

### E.g. of usage

```
$> curl \
  -H "Content-Type: application/json" \
  http://localhost:5000/storage/sensor/add_data \
  -d '{"sensor_id": 1, "angle": "15.5", "temperature": "20.5", "battery": "2.8"}'

{"created": [{"sensor_id": 1, "project_id": 1, "timestamp": 1554034368, "angle": "15.5", "temperature": "20.5", "battery": 2800}]}
```

# TODO

- [x] use sqlite to store the data
- [x] create pages to create projects and sensors
- [x] add _angle_ as float in the parameters
- [ ] set calibration data
- [ ] workout how to compute _gravity_ from _angle_
- [ ] workout how to compute _battery_percent_ from _battery_
- [ ] fix SQL to display sensor when it does not have data (last_active is broken)
- [x] delete datapoints
