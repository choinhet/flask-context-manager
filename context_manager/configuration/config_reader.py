import configparser
import os


class ConfigReader:
    _config = configparser.ConfigParser()
    _current_path = os.path.dirname(__file__)
    _main_file = os.path.join(_current_path, "../resources/config.ini")

    def __init__(self, config_file=None):
        self.config_file = config_file or self._main_file
        self._config.read(self.config_file)

    @property
    def config(self):
        return self._config

    def read_list(self, key, origin=None):
        origin = origin or self._config
        current_item = origin[key]
        return [item.strip() for item in current_item.strip('[]').split(',')]

    def read(self, key, origin=None):
        origin = origin or self._config
        return origin[key]

    def start(self, context_manager, bean):
        ...

    def __hash__(self):
        return hash(self.config_file)

    def __eq__(self, other):
        return self.config_file == other.config_file
