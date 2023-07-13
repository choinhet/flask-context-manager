from decorators import Service


@Service
class HelloService:
    @staticmethod
    def get_hello():
        return "Hello, world!"
