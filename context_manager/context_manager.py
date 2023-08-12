import configparser
import importlib
import inspect
import os
import pkgutil
from functools import partial

from flask import request

from context_manager.config_keys import Contained, BaseKey


class ContextManager:
    beans = dict()
    app = None

    config = configparser.ConfigParser()
    current_path = os.path.dirname(__file__)
    config.read(os.path.join(current_path, "resources/config.ini"))

    imports = [
        config[BaseKey.FOLDERS][Contained.CONTROLLERS],
        config[BaseKey.FOLDERS][Contained.CONFIGURATIONS],
        config[BaseKey.FOLDERS][Contained.SERVICES],
        config[BaseKey.FOLDERS][Contained.MODELS],
        config[BaseKey.FOLDERS][Contained.REPOSITORIES]
    ]

    @classmethod
    def start(cls):
        cls.import_all_modules()
        cls.start_all_modules()
        cls.app.run(debug=True)

    @classmethod
    def import_all_modules(cls):
        for import_name in cls.imports:
            cls.import_modules(import_name)

    @classmethod
    def start_all_modules(cls):
        # cls._order_modules()
        for clz, bean in cls.beans.items():
            clz.start(cls, bean)

    @classmethod
    def import_modules(cls, module_name):
        for _, name, _ in pkgutil.iter_modules([module_name]):
            importlib.import_module(f'{module_name}.{name}')

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
        return type(param.annotation) == type(param.empty)

    @classmethod
    def register_routes(cls, controller):
        prefix = getattr(controller, "_route_prefix", "")
        for method_name, method in inspect.getmembers(controller, predicate=inspect.ismethod):
            route = getattr(method, "_route", None)
            methods = getattr(method, "_methods", None)
            if route is not None and methods is not None:
                wrapped_method = partial(cls._handle_request_body, method)
                wrapped_method.__name__ = method_name + '_wrapped'
                route_path = os.path.join(prefix.rstrip('/'), route.rstrip('/'))
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
