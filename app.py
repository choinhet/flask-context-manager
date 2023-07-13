import importlib
import pkgutil

from flask import Flask

from di_container import DIContainer

app = Flask(__name__)

if __name__ == "__main__":

    print("Starting...")
    DIContainer.start_components()

    print("Registering services...")
    for (_, name, _) in pkgutil.iter_modules(['service']):
        importlib.import_module(f'service.{name}')

    print("Starting services...")
    DIContainer.start_services()

    print("Registering controllers...")
    for (_, name, _) in pkgutil.iter_modules(['controller']):
        importlib.import_module(f'controller.{name}')

    print("Starting controller...")
    DIContainer.start_controllers()

    print("Starting server...")
    app.run(debug=True)
