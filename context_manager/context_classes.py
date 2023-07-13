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
