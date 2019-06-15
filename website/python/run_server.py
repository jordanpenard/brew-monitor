import os

os.environ['BREWMONITOR_CONFIG'] = './debug_config.yaml'

from brewmonitor.app import make_app

app = make_app('secret_key_example')
app.run(debug=True)
