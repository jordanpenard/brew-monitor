import os

from brewmonitor.app import make_app

os.environ['BREWMONITOR_CONFIG'] = './debug_config.yaml'

app = make_app('secret_key_example')
app.run(debug=True)
