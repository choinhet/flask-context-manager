from context_manager.context_classes import Controller
from context_manager.routes import get_mapping, rest_mapping
from service.hello_service import HelloService


@Controller
@rest_mapping('/api/v1')
class HelloController:
    def __init__(self, hello_service: HelloService):
        self.hello_service = hello_service

    @get_mapping('hello')
    def hello(self):
        return self.hello_service.get_hello()
