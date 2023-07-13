from context_manager.di_container import DIContainer


class Component:
    def __init__(self, cls):
        DIContainer.register_component(cls)
        self.decorated_class = cls.__name__


class Service:
    def __init__(self, cls):
        DIContainer.register_service(cls)
        self.decorated_class = cls.__name__


class Controller:
    def __init__(self, cls):
        DIContainer.register_controller(cls)
        self.decorated_class = cls.__name__
