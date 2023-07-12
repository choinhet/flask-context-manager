from flask import Flask

from config.config import Config
from controller.todo_controller import TodoController
from service.db_service import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(TodoController.bp, url_prefix='/api/v1/todo')

if __name__ == '__main__':
    app.run(debug=True)
