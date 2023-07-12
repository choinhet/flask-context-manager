from flask import request, jsonify, Blueprint

from model.todo_item import Todo
from service.db_service import db


class TodoController:
    bp = Blueprint('todo', __name__)

    @staticmethod
    @bp.route("/", methods=["GET"])
    def index():
        try:
            all_todos = Todo.query.order_by(Todo.date_created).all()
            return jsonify([todo.serialize() for todo in all_todos]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @bp.route("/create", methods=["POST"])
    def create_todo(content):
        content = request.json_module.get('content')
        if not content:
            return jsonify({'error': 'Missing content from request'}), 400

        try:
            new_task = Todo(content=content)
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'status': "Todo has been created"}), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @bp.route("/delete/<int:id>", methods=["DELETE"])
    def delete_todo(id):
        try:
            task_to_delete = Todo.query.get_or_404(id)
            db.session.delete(task_to_delete)
            db.session.commit()
            return jsonify({'status': "Todo has been deleted"}), 204
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @bp.route("/update/<int:id>", methods=["PUT"])
    def update_todo(id):
        task = Todo.query.get_or_404(id)
        content = request.json_module.get('content')
        if not content:
            return jsonify({'error': 'Missing content from request'}), 400

        try:
            task.content = content
            db.session.commit()
            return jsonify({'status': "Todo has been updated"}), 204
        except Exception as e:
            return jsonify({'error': str(e)}), 500
