from config.configuration import SQLAlchemySession
from context_manager.beans.repository import Repository


@Repository
class SQLRepository:
    def __init__(self, session: SQLAlchemySession):
        self.session = session.session
