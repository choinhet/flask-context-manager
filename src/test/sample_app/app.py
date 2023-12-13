from flask import Flask

from src.main.core.context_manager import ContextManager

app = Flask(__name__)
ContextManager.append(app)
ContextManager.start()
