import yaml
import sqlite3
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    SQLConnection = sqlite3.Connection


class Configuration:

    def __init__(self, raw_config):
        # type: (Dict) -> None
        self._raw_config = raw_config

    @classmethod
    def load(cls, filename):
        # type: (str) -> Configuration
        return cls(yaml.safe_load(open(filename)))

    @property
    def sqlite_file(self):
        # type: () -> str
        return self._raw_config.get('sqlite file', '/var/run/brewmonitor/database.db')

    def db_connection(self):
        # type: () -> SQLConnection
        return sqlite3.connect(self.sqlite_file)

    @property
    def flask_configuration(self):
        # type: () -> Dict
        return self._raw_config.get('flask configuration', {})
