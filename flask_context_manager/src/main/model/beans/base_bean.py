from abc import ABC

from flask_context_manager.src.main.core.context_manager import ContextManager


class BaseBean(ABC):
    decorated_class = __name__

    def __init__(self, cls):
        self.child_class = cls
        ContextManager.add_bean(cls, self)

    def __hash__(self):
        return hash(self.child_class)

    def __eq__(self, other):
        return getattr(self, "child_class", None) == getattr(other, "child_class", None)
