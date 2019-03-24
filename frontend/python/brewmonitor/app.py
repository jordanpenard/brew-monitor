from flask import Flask
from flask_mako import MakoTemplates

from brewmonitor.storage.views import storage_bp
from brewmonitor.accessor.views import accessor_bp
from brewmonitor.views import home_bp


def make_app(secret_key):
    brewmonitor = Flask(__name__)
    brewmonitor.template_folder = '../../templates/'
    brewmonitor.secret_key = secret_key
    mako = MakoTemplates(brewmonitor)

    brewmonitor.config['MAKO_TRANSLATE_EXCEPTIONS'] = False

    brewmonitor.register_blueprint(home_bp)
    brewmonitor.register_blueprint(accessor_bp)
    brewmonitor.register_blueprint(storage_bp)

    return brewmonitor
