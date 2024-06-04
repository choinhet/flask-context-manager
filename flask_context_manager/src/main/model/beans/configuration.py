import inspect
from typing import TYPE_CHECKING

from flask_context_manager.src.main.core.context_manager import ContextManager
from flask_context_manager.src.main.model.beans.base_bean import BaseBean
from flask_context_manager.src.main.model.beans.bean import Bean


class Configuration(BaseBean):

    def __init__(self, cls):
        super().__init__(cls)
        self.child_class = cls
        ContextManager.add_bean(self.child_class)

        members = inspect.getmembers(self.child_class)
        self.method_beans = self._get_class_beans(members)
        self._add_beans_return_types()

    def _add_beans_return_types(self):
        for bean in self.method_beans:
            ContextManager.add_config_bean(
                bean=bean,
                child_class=self.child_class,
                return_type=bean.fun.__annotations__.get("return")
            )

    @staticmethod
    def _get_class_beans(members):
        method_beans = list(filter(lambda it: issubclass(type(it), Bean), map(lambda it: it[1], members)))
        return method_beans
