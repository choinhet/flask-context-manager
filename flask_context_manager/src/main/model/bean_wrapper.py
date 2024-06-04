from __future__ import annotations

import types
from dataclasses import dataclass
from typing import Generic, Optional, List, Type, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from flask_context_manager.src.main.model.beans.base_bean import BaseBean

T = TypeVar("T")


@dataclass
class NamedParameter:
    clazz: types.MethodType | types.FunctionType
    name: str


@dataclass
class BeanWrapper(Generic[T]):
    bean_name: str
    bean_method: Type[T]
    parameters: List[NamedParameter]
    return_type: Type[T]
    super_class: Optional["BaseBean"] = None
    bean_class: Optional[BeanWrapper] = None
    instance: Optional[T] = None
    is_method: bool = False

    @property
    def dependencies(self):
        class_parameters = list()
        if self.bean_class:
            class_parameters = self.bean_class.parameters
        return self.parameters + class_parameters

    def __hash__(self):
        return hash((self.bean_name, self.bean_method, self.return_type, self.bean_class))

    def __eq__(self, other):
        if not isinstance(other, BeanWrapper):
            return False

        return self.bean_name != other.bean_name \
            or self.bean_method != other.bean_method \
            or self.parameters != other.parameters \
            or self.return_type != other.return_type \
            or self.bean_class != other.bean_class
