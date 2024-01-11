from setuptools import setup, find_packages

setup(
    name='flask-context-manager',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/rxonhe/flask-context-manager',
    license='MIT',
    author='Rafael Choinhet',
    author_email='choinhet@gmail.com',
    description='A lightweight dependency injection and route management system for Flask, inspired by Spring Boot.',
    long_description="""
    # Flask Context Manager

    The Flask Context Manager is a project that provides an inversion of control (IoC) container for Flask applications. It offers features reminiscent of the Spring Boot framework, including dependency injection, route management, configuration reading, and more.
    
    ## Features
    
    - **Dependency Injection**: Enjoy automatic dependency injection. Classes with `@Service`, `@Controller`, or `@Component` are managed automatically, and their dependencies are resolved via constructors.
    
    - **Route Management**: Define routes at the method level using `@get_mapping`, `@post_mapping`, `@put_mapping`, `@delete_mapping`. The `@rest_mapping` adds a prefix to all routes in a controller.
    
    - **Dynamic URL Handling**: With dynamic URL routing, methods can easily fetch parameters from URLs.
    
    - **POST Method Parameters**: Design POST methods effortlessly by specifying parameters directly in the method.
    
    - **Configuration Reading**: Extract values from configuration files seamlessly. Use `@auto_set_key` for auto-generating keys to access configurations.

""",
    long_description_content_type='text/markdown',
    install_requires=['flask>=3.0.0'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
