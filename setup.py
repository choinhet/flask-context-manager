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
    install_requires=['flask>=3.0.0'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
