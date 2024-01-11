from flask_context_manager.src.main.core.routes import get_mapping, rest_mapping, post_mapping
from flask_context_manager.src.main.model.beans.controller import Controller
from flask_context_manager.src.test.sample_app.service.hello_service import HelloService


@Controller
@rest_mapping('/api/v1')
class HelloController:
    def __init__(self, hello_service: HelloService):
        self.hello_service = hello_service

    @get_mapping('hello')
    def hello(self):
        return self.hello_service.get_hello()

    @post_mapping('hi')
    def hi(self, hi):
        return hi
