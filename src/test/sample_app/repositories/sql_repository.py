from config.configuration import SQLAlchemySession
from src.main.model.beans.repository import Repository


@Repository
class SQLRepository:
    def __init__(self, session: SQLAlchemySession):
        self.session = session.session
