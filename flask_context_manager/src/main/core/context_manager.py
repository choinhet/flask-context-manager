import importlib
import inspect
import os
from functools import partial

from flask import request

from flask_context_manager.src.main.configuration.config_reader import ConfigReader
from flask_context_manager.src.main.model.config_keys import BaseKey


class ContextManager:
    beans = dict()
    reader = ConfigReader()
    beans[ConfigReader] = reader
    app = None

    @classmethod
    def set_reader(cls, reader):
        cls.reader = reader
        cls.beans[ConfigReader] = reader

    @classmethod
    def start(cls):
        folders = cls.reader.read(BaseKey.FOLDERS)
        ignore_patterns = cls.reader.read_list(BaseKey.IGNORE, origin=folders)
        cls.import_all_modules(ignore_patterns=ignore_patterns)
        cls.start_all_modules()
        cls.app.run(debug=True)

    @staticmethod
    def is_ignored(path, ignore_patterns):
        return any(pattern in path for pattern in ignore_patterns)

    @staticmethod
    def get_module_name_from_path(path):
        rel_path = os.path.relpath(path).replace(os.sep, '.')
        module_name, _ = os.path.splitext(rel_path)
        return module_name

    @classmethod
    def import_module_from_path(cls, file_path):
        module_name = cls.get_module_name_from_path(file_path)
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")

    @classmethod
    def import_all_modules(cls, root_dir=".", ignore_patterns=None):
        for dir_path, _, filenames in os.walk(root_dir):
            if cls.is_ignored(dir_path, ignore_patterns or []):
                continue

            for filename in filenames:
                if filename.endswith('.py') and not cls.is_ignored(filename, ignore_patterns):
                    file_path = os.path.join(dir_path, filename)
                    cls.import_module_from_path(file_path)

    @classmethod
    def start_all_modules(cls):
        # cls._order_modules()
        for clz, bean in cls.beans.items():
            clz.start(cls, bean)

    @classmethod
    def accept(cls, dict_to_accept):
        cls.beans.update(dict_to_accept)

    @classmethod
    def get_injections(cls, obj):
        sig = inspect.signature(obj.__init__)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name == 'self' or ContextManager._inspection_is_empty(param):
                continue
            annotation = obj.__init__.__annotations__[name].child_class
            kwargs[name] = cls._get_dependency(annotation, obj)
        return kwargs

    @classmethod
    def _inspection_is_empty(cls, param):
        return param.annotation == param.empty

    @classmethod
    def is_function_or_method(cls, element):
        return inspect.isfunction(element) or inspect.ismethod(element)

    @classmethod
    def register_routes(cls, controller):
        prefix = getattr(controller, "_route_prefix", "")
        for method_name, method in inspect.getmembers(controller, predicate=cls.is_function_or_method):
            route = getattr(method, "_route", None)
            methods = getattr(method, "_methods", None)
            if route is not None and methods is not None:
                wrapped_method = partial(cls._handle_request_body, method)
                wrapped_method.__name__ = method_name + '_wrapped'
                paths = prefix.split('/') + route.split('/')
                paths = [p for p in paths if p != ""]
                route_path = "/" + "/".join(paths)
                cls.app.route(route_path, methods=methods)(wrapped_method)

    @classmethod
    def append(cls, app):
        cls.app = app
        return cls

    @classmethod
    def get_app(cls):
        return cls.app

    @classmethod
    def _get_dependency(cls, annotation, obj):

        if annotation == obj:
            raise RuntimeError(f"Circular dependency detected for service {obj.__name__}")

        instantiated_beans = [bean for bean in cls.beans.values() if type(bean) != type]
        dependency_dict = {bean.__class__: bean for bean in instantiated_beans}

        if annotation in dependency_dict.keys():
            return dependency_dict[annotation]

        try:
            if annotation in cls.beans.keys():
                return cls.beans[annotation].start(cls, cls.beans[annotation])
        except RuntimeError:
            raise RuntimeError(f"Dependency {annotation} not found for object {obj.__name__}")

    @staticmethod
    def _handle_request_body(method, *args, **kwargs):
        if request.method != 'GET':
            request_body = request.json or {}
            new_kwargs = {param: request_body.get(param, None) for param in inspect.signature(method).parameters}
            new_kwargs.update(kwargs)
        else:
            new_kwargs = kwargs
        return method(*args, **new_kwargs)
