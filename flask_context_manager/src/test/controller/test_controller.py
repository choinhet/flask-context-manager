from flask_context_manager import Controller, rest_mapping, get_mapping
from flask_context_manager.src.test.service.test_service import TestService


@Controller
@rest_mapping("test")
class TestController:

    def __init__(self, test_service: TestService):
        self.test_service = test_service

    @get_mapping("first")
    def first(self):
        return self.test_service.say_test()
