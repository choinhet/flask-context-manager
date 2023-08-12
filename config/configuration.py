from flask_sqlalchemy import SQLAlchemy

from context_manager.beans.configuration import Configuration


@Configuration
class SQLAlchemySession:
    def __init__(self, app):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        self.db = SQLAlchemy(self.app)

    @property
    def session(self):
        return self.db.session
