from datetime import datetime
from service.db_service import db


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'completed': self.completed,
            'date_created': self.date_created
        }
