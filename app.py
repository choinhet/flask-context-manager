from flask import Flask

from context_manager.di_container import DIContainer

app = Flask(__name__)

if __name__ == "__main__":
    DIContainer.append(app).start()
