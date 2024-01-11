from flask_context_manager.src.main.model.beans.service import Service


@Service
class HelloService:
    @staticmethod
    def get_hello():
        return "Hello, world!"
