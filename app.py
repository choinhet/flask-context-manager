from flask import Flask

from context_manager.context_manager import ContextManager

app = Flask(__name__)

if __name__ == "__main__":
    ContextManager.append(app).start()
