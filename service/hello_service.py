from context_manager.context_classes import Service


@Service
class HelloService:
    @staticmethod
    def get_hello():
        return "Hello, world!"
