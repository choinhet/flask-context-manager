import importlib
import inspect
import os
import pkgutil
from flask import request


class ContextManager:
    components = dict()
    services = dict()
    controllers = dict()
    models = dict()
    repositories = dict()
    configurations = dict()
    app = None

    @classmethod
    def start(cls):
        cls.import_modules('controller')
        cls.import_modules('config')
        cls.import_modules('service')
        cls.import_modules('model')
        cls.import_modules('repositories')

        cls.start_components()
        cls.start_configurations()
        cls.start_repositories()
        cls.start_services()
        cls.start_controllers()

        cls.app.run(debug=True)

    @classmethod
    def import_modules(cls, module_name):
        for _, name, _ in pkgutil.iter_modules([module_name]):
            importlib.import_module(f'{module_name}.{name}')

    @classmethod
    def register_component(cls, instance):
        cls.components[instance.__name__] = instance

    @classmethod
    def register_service(cls, instance):
        cls.services[instance.__name__] = instance

    @classmethod
    def register_controller(cls, instance):
        cls.controllers[instance.__name__] = instance

    @classmethod
    def register_model(cls, instance):
        cls.models[instance.__name__] = instance

    @classmethod
    def register_repository(cls, repository):
        cls.repositories[repository.__name__] = repository

    @classmethod
    def register_configuration(cls, instance):
        cls.configurations[instance.__name__] = instance

    @classmethod
    def start_configurations(cls):
        for key, configuration in cls.configurations.items():
            sig = inspect.signature(configuration.__init__)
            params = sig.parameters
            kwargs = {'app': cls.app} if 'app' in params else {}
            instance = configuration(**kwargs)
            cls.configurations[key] = instance

    @classmethod
    def start_components(cls):
        for key, component in cls.components.items():
            cls.components[key] = component()

    @classmethod
    def start_repositories(cls):
        dependency_dict_list = [cls.services, cls.repositories, cls.configurations, cls.components]
        for key, repository in cls.repositories.items():
            kwargs = cls.get_constructor_arguments(repository, dependency_dict_list)
            cls.repositories[key] = repository(**kwargs)

    @classmethod
    def start_services(cls):
        dependency_dict_list = [cls.services, cls.repositories, cls.configurations, cls.components]
        for key, service in cls.services.items():
            kwargs = cls.get_constructor_arguments(service, dependency_dict_list)
            cls.services[key] = service(**kwargs)

    @classmethod
    def start_controllers(cls):
        dependency_dict_list = [cls.services, cls.repositories, cls.configurations, cls.components]
        for key, controller in cls.controllers.items():
            kwargs = cls.get_constructor_arguments(controller, dependency_dict_list)
            cls.controllers[key] = controller(**kwargs)
            cls.register_controller_routes(cls.controllers[key])

    @classmethod
    def get_constructor_arguments(cls, obj, dependency_dict_list):
        sig = inspect.signature(obj.__init__)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name == 'self' or param.annotation == param.empty:
                continue
            cls.validate_annotation(obj, name, param, dependency_dict_list)
            annotation = obj.__init__.__annotations__[name].decorated_class
            kwargs[name] = cls.get_dependency(annotation, obj, dependency_dict_list)
        return kwargs

    @classmethod
    def validate_annotation(cls, obj, name, param, dependency_dict_list):
        for dependency_dict in dependency_dict_list:
            if obj.__init__.__annotations__[name].decorated_class in dependency_dict:
                return
        raise RuntimeError(f"Dependency {param.annotation} not found for object {obj.__name__}")

    @classmethod
    def get_dependency(cls, annotation, obj, dependency_dict_list):
        for dependency_dict in dependency_dict_list:
            if annotation in dependency_dict:
                if annotation == obj:
                    raise RuntimeError(f"Circular dependency detected for service {obj.__name__}")
                return dependency_dict[annotation]
        raise RuntimeError(f"Dependency {annotation} not found for object {obj.__name__}")

    @classmethod
    def register_controller_routes(cls, controller):
        prefix = getattr(controller, "_route_prefix", "")
        for method_name, method in inspect.getmembers(controller, predicate=inspect.ismethod):
            route = getattr(method, "_route", None)
            methods = getattr(method, "_methods", None)
            if route is not None and methods is not None:
                def method_with_request_body(*args, **kwargs):
                    request_body = request.json or {}
                    new_kwargs = {param: request_body.get(param, None) for param in inspect.signature(method).parameters}
                    new_kwargs.update(kwargs)
                    return method(*args, **new_kwargs)
                cls.app.route(os.path.join(prefix.rstrip('/'), route), methods=methods)(method_with_request_body)


    @classmethod
    def append(cls, app):
        cls.app = app
        return cls

    @classmethod
    def get_app(cls):
        return cls.app
