from flask import Flask
from context_manager.context_manager import ContextManager

app = Flask(__name__)
ContextManager.append(app)

if __name__ == "__main__":
    ContextManager.start()
    app.run(debug=True)
