# Flask Context Manager

The Flask Context Manager is a project that provides an inversion of control (IoC) container for Flask applications. It offers features similar to the Spring Boot framework, including dependency injection and route management.

## Features

- **Dependency Injection**: The Context Manager supports automatic dependency injection. It allows you to annotate classes with `@Service`, `@Controller`, or `@Component` and automatically manages their lifecycle. These instances can be injected into other classes through the constructor, reducing the need for manual wiring.

- **Route Management**: The Context Manager also offers route annotations similar to Spring Boot. You can use `@get_mapping`, `@post_mapping`, `@put_mapping`, and `@delete_mapping` to define routes at the method level.

- **Rest Mapping**: The `@rest_mapping` decorator allows you to add a prefix to all routes in a controller.

## Usage

To use the Context Manager, your application should have separate directories for services (`/service`), controllers (`/controller`), and components (`/component`).

Here's an example of how you might define a service and a controller:

```python
# service/hello_service.py
from context_manager.context_classes import service

@Service
class HelloService:
    def get_hello(self):
        return "Hello, World!"

# controller/hello_controller.py
from context_manager.context_classes import controller
from context_manager.routes import get_mapping
from service.hello_service import HelloService

@Controller
@rest_mapping('/api/v1')
class HelloController:
    def __init__(self, hello_service: HelloService):
        self.hello_service = hello_service

    @get_mapping('hello')
    def hello(self):
        return self.hello_service.get_hello()

```

In your main application file, you need to start the Context Manager before running the Flask application:

```python
from flask import Flask
from context_manager.context_manager import ContextManager

app = Flask(__name__)
ContextManager.append(app)

if __name__ == "__main__":
    ContextManager.start()
    app.run(debug=True)
```

## Requirements

This project requires Python 3.6+ and Flask.

Please note that this project is for educational purposes and may not be suitable for production use. Always thoroughly test and review the code before using it in a production environment.