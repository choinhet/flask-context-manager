from abc import ABC, abstractmethod

from context_manager.context_manager import ContextManager


class BaseBean(ABC):
    decorated_class = __name__

    def __init__(self, cls):
        self.child_class = cls
        ContextManager.accept({self: cls})

    @abstractmethod
    def start(self, context, bean):
        ...

    def __hash__(self):
        return hash(self.child_class)

    def __eq__(self, other):
        return self.child_class == other.child_class
