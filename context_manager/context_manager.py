import importlib
import inspect
import os
import pkgutil


class ContextManager:
    components = dict()
    services = dict()
    controllers = dict()
    app = None

    @classmethod
    def start(cls):
        cls.start_components()
        cls.import_modules('service')
        cls.start_services()
        cls.import_modules('controller')
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
    def start_components(cls):
        for key, component in cls.components.items():
            cls.components[key] = component()

    @classmethod
    def start_services(cls):
        for key, service in cls.services.items():
            kwargs = cls.get_constructor_arguments(service, cls.services, cls.components)
            cls.services[key] = service(**kwargs)

    @classmethod
    def start_controllers(cls):
        for key, controller in cls.controllers.items():
            kwargs = cls.get_constructor_arguments(controller, cls.services, cls.components)
            cls.controllers[key] = controller(**kwargs)
            cls.register_controller_routes(cls.controllers[key])

    @classmethod
    def get_constructor_arguments(cls, obj, services, components):
        sig = inspect.signature(obj.__init__)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
            if param.annotation != inspect._empty:
                annotation = obj.__init__.__annotations__[name].decorated_class
                if annotation in services:
                    if param.annotation == obj:
                        raise RuntimeError(f"Circular dependency detected for service {obj.__name__}")
                    kwargs[name] = services[annotation]
                elif annotation in components:
                    kwargs[name] = components[annotation]
                else:
                    raise RuntimeError(f"Dependency {param.annotation} not found for object {obj.__name__}")
        return kwargs

    @classmethod
    def register_controller_routes(cls, controller):
        prefix = getattr(controller, "_route_prefix", "")
        for method_name, method in inspect.getmembers(controller, predicate=inspect.ismethod):
            route = getattr(method, "_route", None)
            methods = getattr(method, "_methods", None)
            if route is not None and methods is not None:
                cls.app.route(os.path.join(prefix.rstrip('/'), route), methods=methods)(method)

    @classmethod
    def append(cls, app):
        cls.app = app
        return cls

    @classmethod
    def get_app(cls):
        return cls.app
