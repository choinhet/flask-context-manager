from config.configuration import SQLAlchemySession
from context_manager.context_classes import Repository


@Repository
class SQLRepository:
    def __init__(self, session: SQLAlchemySession):
        self.session = session.session
