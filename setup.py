import sys

from setuptools import setup, find_packages

VERSION = "1.0.12"

with open("README.md", "r") as fh:
    readme = fh.read()
    fh.close()

if sys.version_info.major != 3 and sys.version_info.minor < 10:
    sys.exit("'Flask Context Manager' requires Python >= 3.10!")

setup(
    name="flask-context-manager",
    version=VERSION,
    packages=find_packages(),
    url="https://github.com/rxonhe/flask-context-manager",
    license="MIT",
    author="Rafael Choinhet",
    author_email="choinhet@gmail.com",
    description="A lightweight dependency injection and route management system for Flask, inspired by Spring Boot.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["flask>=3.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        flask_context_manager=flask_context_manager.flask_context_manager:main
    """,
    python_requires=">=3.10",
    include_package_data=True,
    package_data={"": ["*.ttf", "*.png", "*.pdf", "*.jar", "*.json", "*.ini"]}

)
