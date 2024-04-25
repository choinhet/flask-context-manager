from __future__ import annotations

import configparser
import os

from flask_context_manager import Component


@Component
class ConfigReader:

    @classmethod
    def start(cls, context, bean):
        context.beans[cls] = bean

    _config = configparser.ConfigParser()
    _current_path = os.path.dirname(__file__)
    _main_file = os.path.join(_current_path, "../resources/config.ini")
    root_dir = os.path.dirname(os.path.dirname(__file__))

    def __init__(self, config_file=None):
        self.config_file = config_file or self._main_file
        self._config.read(self.config_file)
        self.child_class = self

    def set_path_from_root(self, path):
        self.config_file = os.path.join(self.root_dir, path.removeprefix("/"))
        self._config.read(self.config_file)

    @property
    def config(self):
        return self._config

    def read_list(self, key, origin=None):
        origin = origin or self._config
        current_item = origin[key]
        return [item.strip() for item in current_item.strip('[]').split(',')]

    def read(self, *keys, origin=None, default=None):
        try:
            origin = origin or self._config
            for key in keys:
                origin = origin[key]
            return origin
        except KeyError:
            return default

    def __hash__(self):
        return hash(self.config_file)

    def __eq__(self, other):
        return self.config_file == other.config_file


ConfigReader.child_class = ConfigReader
