import os

from brewmonitor.app import make_app


# This is an example file to run the server as debug.
# In production use an actual env variable from your setup (e.g. /etc/environment).
os.environ['BREWMONITOR_CONFIG'] = './debug_config.yaml'

app = make_app('secret_key_example')
app.run(debug=True)
