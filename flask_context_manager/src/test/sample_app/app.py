from flask import Flask

from flask_context_manager import ContextManager

app = Flask(__name__)
ContextManager.append(app)
ContextManager.start()
