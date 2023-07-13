from context_manager.context_classes import Controller
from context_manager.routes import get_mapping
from service.hello_service import HelloService


@Controller
class HelloController:
    def __init__(self, hello_service: HelloService):
        self.hello_service = hello_service

    @get_mapping('/api/v1/hello')
    def hello(self):
        return self.hello_service.get_hello()
