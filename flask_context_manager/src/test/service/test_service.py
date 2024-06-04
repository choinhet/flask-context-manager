from flask_context_manager import Service
from flask_context_manager.src.test.configuration.test_configuration import TestInstance


@Service
class TestService:
    def __init__(self, my_test_instance: TestInstance):
        self.my_test_instance = my_test_instance

    @staticmethod
    def say_test():
        return "Test!!!!"
