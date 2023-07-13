import importlib
import inspect
import pkgutil


class DIContainer:
    components = dict()
    services = dict()
    controllers = dict()
    app = None

    @classmethod
    def start(cls):
        DIContainer.start_components()
        for (_, name, _) in pkgutil.iter_modules(['service']):
            importlib.import_module(f'service.{name}')
        DIContainer.start_services()
        for (_, name, _) in pkgutil.iter_modules(['controller']):
            importlib.import_module(f'controller.{name}')
        DIContainer.start_controllers()
        cls.app.run(debug=True)

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
            instance = component()
            cls.components[key] = instance

    @classmethod
    def start_services(cls):
        for key, service in cls.services.items():
            sig = inspect.signature(service.__init__)
            kwargs = {}
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                if param.annotation != inspect._empty:
                    if param.annotation in cls.services:
                        if param.annotation == service:
                            raise RuntimeError(f"Circular dependency detected for service {key}")
                        kwargs[name] = cls.services[param.annotation]
                    elif param.annotation in cls.components:
                        kwargs[name] = cls.components[param.annotation]
                    else:
                        raise RuntimeError(f"Dependency {param.annotation} not found for service {key}")
            instance = service(**kwargs)
            cls.services[key] = instance

    @classmethod
    def start_controllers(cls):
        for key, controller in cls.controllers.items():
            sig = inspect.signature(controller.__init__)
            kwargs = {}
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                if param.annotation != inspect._empty:
                    annotation = controller.__init__.__annotations__[name].decorated_class
                    if annotation in cls.controllers:
                        raise RuntimeError(f"Controller {key} can't depend on other controller")
                    elif annotation in cls.services:
                        kwargs[name] = cls.services[annotation]
                    elif annotation in cls.components:
                        kwargs[name] = cls.components[annotation]
                    else:
                        raise RuntimeError(f"Dependency {param.annotation} not found for controller {key}")
            instance = controller(**kwargs)
            cls.controllers[key] = instance

            for method_name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
                route = getattr(method, "_route", None)
                methods = getattr(method, "_methods", None)
                if route is not None and methods is not None:
                    cls.app.route(route, methods=methods)(method)

    @classmethod
    def append(cls, app):
        cls.app = app

    @classmethod
    def get_app(cls):
        return cls.app
