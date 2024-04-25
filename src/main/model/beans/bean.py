from typing import TypeVar, Type, Generic

T = TypeVar('T')


class Bean(Generic[T]):

    def __init__(self, fun: Type[T]):
        self.fun = fun

    def __call__(self, *args, **kwargs) -> T:
        return self.fun(*args, **kwargs)
