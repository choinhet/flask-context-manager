from context_manager.context_manager import ContextManager


class Component:
    def __init__(self, cls):
        ContextManager.register_component(cls)
        self.decorated_class = cls.__name__


class Service:
    def __init__(self, cls):
        ContextManager.register_service(cls)
        self.decorated_class = cls.__name__


class Controller:
    def __init__(self, cls):
        ContextManager.register_controller(cls)
        self.decorated_class = cls.__name__


class Configuration:
    def __init__(self, cls):
        ContextManager.register_configuration(cls)
        self.decorated_class = cls.__name__


class Model:
    def __init__(self, cls):
        ContextManager.register_model(cls)
        self.decorated_class = cls.__name__


class Repository:
    def __init__(self, cls):
        ContextManager.register_repository(cls)
        self.decorated_class = cls.__name__
