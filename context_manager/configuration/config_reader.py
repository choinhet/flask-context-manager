import configparser
import os


class ConfigReader:
    _config = configparser.ConfigParser()
    _current_path = os.path.dirname(__file__)
    _config.read(os.path.join(_current_path, "../resources/config.ini"))

    @property
    def config(self):
        return self._config
