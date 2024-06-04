from flask_context_manager import ContextManager
from flask_context_manager.src.main.model.beans.base_bean import BaseBean


class Controller(BaseBean):

    def __init__(self, cls):
        super().__init__(cls)
        ContextManager.register_routes(self.child_class)
