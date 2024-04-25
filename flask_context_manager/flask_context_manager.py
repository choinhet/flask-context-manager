import argparse
import os


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_file(path, content=""):
    with open(path, 'w') as file:
        file.write(content)
        file.close()


def add_init_file(path):
    init_path = os.path.join(path, '__init__.py')
    create_file(init_path)


def setup_project_structure():
    base_dirs = [
        'src',

        'src/main',
        'src/test',

        'src/main/config',
        'src/main/service',
        'src/main/controller',
        'src/main/resources',

        'src/test/config',
        'src/test/service',
        'src/test/controller',
        'src/test/resources'
    ]

    for dir_ in base_dirs:
        create_directory(dir_)
        add_init_file(dir_)

    app_content = (
        "from flask import Flask\n\n"
        "from flask_context_manager import ContextManager\n\n"
        "app = Flask(__name__)\n"
        "ContextManager.append(app)\n\n"
        "if __name__ == '__main__':\n"
        "    ContextManager.start(debug=True)\n"
    )

    create_file('app.py', app_content)

    print("Flask Context Manager structure successfully created!")


def main():
    parser = argparse.ArgumentParser(description='Flask Context Manager CLI')
    parser.add_argument('command', choices=['start'], help='Command to execute')

    args = parser.parse_args()

    if args.command == 'start':
        setup_project_structure()


if __name__ == "__main__":
    main()
