import os

from flask import Flask
from flask_mako import MakoTemplates

from brewmonitor.accessor.views import accessor_bp
from brewmonitor.admin.views import admin_bp
from brewmonitor.configuration import Configuration
from brewmonitor.schema import initialise_db
from brewmonitor.storage.views import storage_bp
from brewmonitor.views import home_bp
from brewmonitor.user import User

from flask_login import LoginManager


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
    brewmonitor.register_blueprint(admin_bp)
    
    login_manager = LoginManager()
    login_manager.login_view = 'home.index'
    login_manager.init_app(brewmonitor)

    @login_manager.user_loader
    def load_user(id):
    	return User.from_db(config.db_connection(), int(id))
    
    return brewmonitor
