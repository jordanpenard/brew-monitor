import os
from copy import deepcopy
from datetime import datetime
from tempfile import NamedTemporaryFile

import pytest
import yaml
from flask import Flask

from brewmonitor.app import make_app
from brewmonitor.configuration import Configuration
from make_dummy_data import make_dummy_data

test_config = {
    'flask configuration': {
        'TESTING': True,
        'SERVER_NAME': 'unit-test-brewmonitor.domain',
    },
}


def config_from_client(client_obj: Flask) -> Configuration:
    return client_obj.config['brewmonitor config']


def make_clean_client(config_file: NamedTemporaryFile, db_file: NamedTemporaryFile) -> Flask:
    apply_config = deepcopy(test_config)
    apply_config['sqlite file'] = db_file.name

    yaml.dump(apply_config, config_file.file, encoding='utf-8')

    os.environ['BREWMONITOR_CONFIG'] = config_file.name

    print(f'Making app with config={config_file.name} and db={db_file.name}')
    return make_app('unit test secrets')


@pytest.fixture(scope='function')
def tmp_app() -> Flask:
    """Creates a clean db every time and destroys it at the end of the test."""
    with NamedTemporaryFile() as config_file:
        with NamedTemporaryFile() as db_file:
            yield make_clean_client(config_file, db_file)


preset_when = datetime(2021, 11, 26, 11, 34)


@pytest.fixture(scope='package')
def preset_app() -> Flask:
    """
    Creates a clean db but keeps it in between tests. Remember to clean if modified.
    Returns the app, the test client is not created and the app_context is not initialised.
    """
    with NamedTemporaryFile() as config_file:
        with NamedTemporaryFile() as db_file:
            app = make_clean_client(config_file, db_file)
            bm_config = config_from_client(app)
            make_dummy_data(bm_config, 'admin', when=preset_when)
            yield app
