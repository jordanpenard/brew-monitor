import yaml
import sqlite3
from typing import Dict

from flask import current_app

SQLConnection = sqlite3.Connection


class Configuration:

    def __init__(self, raw_config: Dict):
        self._raw_config = raw_config

    @classmethod
    def load(cls, filename: str) -> "Configuration":
        return cls(yaml.safe_load(open(filename)))

    @property
    def sqlite_file(self) -> str:
        return self._raw_config.get('sqlite file', '/var/run/brewmonitor/database.db')

    def db_connection(self) -> SQLConnection:
        return sqlite3.connect(self.sqlite_file)

    @property
    def flask_configuration(self) -> Dict:
        return self._raw_config.get('flask configuration', {})


def config() -> Configuration:
    return current_app.config['brewmonitor config']