import logging
import os
from functools import cached_property
from types import ModuleType
from typing import Optional, Any, Dict

log = logging.getLogger()


class RelativePath(str):
    origin = os.path.dirname(__file__)

    def __init__(self, path: str):
        self.path = os.path.join(self.origin, path.removeprefix("/"))

    def set_path(self, path):
        self.path = path

    def write_text(self, text):
        with open(self.path, "w") as f:
            f.write(text)
            f.close()

    def read_text(self) -> Optional[str]:
        try:
            with open(self.path, "r") as f:
                text = f.read()
                f.close()
        except FileNotFoundError:
            text = None
        return text

    def read_lines(self) -> Optional[list[str]]:
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
                f.close()
        except FileNotFoundError:
            lines = None
        return lines

    def read_json(self) -> Optional[Dict[str, Any]]:
        import json
        try:
            with open(self.path, "r", encoding='utf-8') as f:
                json_obj = json.load(f)
                f.close()
        except FileNotFoundError:
            log.error(f"File not found: {self.path}")
            json_obj = None
        except Exception as e:
            log.error(f"Error reading json file: {self.path}\nCause:{e}")
            json_obj = None
        return json_obj

    def read_py(self) -> Optional[ModuleType]:
        import importlib.util
        spec = importlib.util.spec_from_file_location(self._get_module_name_from_path, self.path)
        if spec is None or spec.loader is None:
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @cached_property
    def _get_module_name_from_path(self):
        base_name = os.path.basename(self.path)
        return os.path.splitext(base_name)[0]

    def write_json(self, json_obj):
        import json
        with open(self.path, "w") as f:
            json.dump(json_obj, f, indent=4)
            f.close()

    def join(self, *paths):
        paths_without_prefix = [path.removeprefix("/") for path in paths]
        return RelativePath(os.path.join(str(self.path), *paths_without_prefix))

    def delete(self):
        os.remove(self.path)

    def prefix(self, prefix):
        return RelativePath(os.path.join(prefix, str(self.path)))

    def list_files(self):
        return [RelativePath(os.path.join(self.path, file)) for file in os.listdir(self.path)]

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def name(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path
