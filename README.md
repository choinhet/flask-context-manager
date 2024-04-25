# Flask Context Manager

The Flask Context Manager is a project that provides an inversion of control (IoC) container for Flask applications. It offers features reminiscent of the Spring Boot framework, including dependency injection, route management, configuration reading, and more.

## Installation

```bash
pip install flask-context-manager
```

## Initialization (Optional)

In the terminal, run the following command to initialize folder structure:

```bash
flask_context_manager start
```

## Features

- **Dependency Injection**: Enjoy automatic dependency injection. Classes with `@Service`, `@Controller`, or `@Component` are managed automatically, and their dependencies are resolved via constructors.

- **Route Management**: Define routes at the method level using `@get_mapping`, `@post_mapping`, `@put_mapping`, `@delete_mapping`. The `@rest_mapping` adds a prefix to all routes in a controller.

- **Dynamic URL Handling**: With dynamic URL routing, methods can easily fetch parameters from URLs.

- **POST Method Parameters**: Design POST methods effortlessly by specifying parameters directly in the method.

## Usage

Structure your application with directories for services (`/service`), controllers (`/controller`), and components (`/component`).

### Basic Example

`service/hello_service.py`
```python
@Service
class HelloService:
    
    def get_hello(self):
        return "Hello, World!"
```

`controller/hello_controller.py`
```python
@Controller
@rest_mapping('/api/v1')
class HelloController:
    
    def __init__(self, hello_service: HelloService):
        self.hello_service = hello_service

    @get_mapping('hello')
    def hello(self):
        return self.hello_service.get_hello()
```

### Configuration

Similar to Spring Boot, we can add the `@Configuration` annotation so that any annotated `@Bean` methods are automatically registered in the context as soon as it starts.

`config/app_config.py`
```python
@Configuration
class AppConfig:
    
    @Bean
    def my_jackson_copy(self):
        return MyJacksonCopy()

    @Bean
    def i_just_run_and_return_nothing_and_its_ok(self):
        print("First!!!")
```


## Handling Dynamic URL Parameters:

The Flask Context Manager supports dynamic parameters in routes just like native Flask. To capture a portion of the URL as a variable, you can use the `<variable_name>` syntax in your mapping.

### Example:

`controller/user_controller.py`
```python
@Controller
@rest_mapping('/api/v1')
class UserController:

    @get_mapping('user/<user_id>')
    def get_user_by_id(self, user_id):
        return f"Fetching info for user with ID: {user_id}"
```

### POST Method with Direct Parameters:

`controller/test_controller.py`
```python
@Controller
class TestController:

    @post_mapping("/test")
    def my_post(body):
        return "This is a cool body:" + str(body)
```

### Starting the Application:

In the main application file, initiate the Context Manager:

`app.py`

```python
from flask import Flask
from flask_context_manager.src.main.core.context_manager import ContextManager

app = Flask(__name__)
ContextManager.append(app)

if __name__ == "__main__":
    ContextManager.start()
```

## Requirements

- Python 3.6+ 
- Flask

> **Note**: This project is mainly for educational purposes. Ensure thorough testing and code review before deploying in a production setting.
