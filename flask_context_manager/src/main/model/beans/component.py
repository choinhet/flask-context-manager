from typing import TypeVar, Type, Generic

from flask_context_manager.src.main.model.beans.base_bean import BaseBean

T = TypeVar('T')


class Component(BaseBean, Generic[T]):

    def __init__(self, cls: Type[T]):
        self._cls = cls
        super().__init__(cls)

    def __call__(self, *args, **kwargs) -> T:
        return self._cls(*args, **kwargs)

    def start(self, context, bean):
        kwargs = context.get_injections(bean)
        context.beans[self.child_class] = bean(**kwargs)
