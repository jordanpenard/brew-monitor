import os

from flask import Flask
from flask_mako import MakoTemplates

from brewmonitor.accessor.views import accessor_bp
from brewmonitor.configuration import Configuration
from brewmonitor.schema import initialise_db
from brewmonitor.storage.views import storage_bp
from brewmonitor.views import home_bp


def make_app(secret_key):
    brewmonitor = Flask(__name__)
    brewmonitor.template_folder = '../../templates/'
    brewmonitor.secret_key = secret_key
    _ = MakoTemplates(brewmonitor)

    config = Configuration.load(
        os.environ.get('BREWMONITOR_CONFIG', '/usr/local/brewmonitor/configuration.yaml')
    )
    brewmonitor.config.update(
        config.flask_configuration
    )
    # Ensure that at least that option is off
    brewmonitor.config['MAKO_TRANSLATE_EXCEPTIONS'] = False
    brewmonitor.config['brewmonitor config'] = config

    initialise_db(config)

    brewmonitor.register_blueprint(home_bp)
    brewmonitor.register_blueprint(accessor_bp)
    brewmonitor.register_blueprint(storage_bp)

    return brewmonitor
