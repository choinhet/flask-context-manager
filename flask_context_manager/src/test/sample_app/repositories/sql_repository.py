from config.configuration import SQLAlchemySession
from flask_context_manager.src.main.model.beans.repository import Repository


@Repository
class SQLRepository:
    def __init__(self, session: SQLAlchemySession):
        self.session = session.session
