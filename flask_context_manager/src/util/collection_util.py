from typing import Dict, TypeVar, Callable, Iterable, List, Optional, Hashable

T = TypeVar("T")
K = TypeVar("K")


def get_or_put(current_dict: Dict[Hashable, T], key: Hashable, put: Callable[[], T]) -> T:
    if key not in current_dict:
        current_dict[key] = put()
    return current_dict[key]


def flat_map(iterable: Iterable[Iterable[K]], function: Callable[[K], T]) -> List[T]:
    destination: List[T] = list()
    for item in iterable:
        list_ = list(map(function, item))
        destination.extend(list_)
    return destination


def first_or_none(iterable: Iterable[T], predicate: Callable[[T], bool] = lambda _: True) -> Optional[T]:
    for item in iterable:
        if predicate(item):
            return item


def flatten(iterable: Iterable[Iterable[T]]) -> List[T]:
    destination: List[T] = list()
    for item in iterable:
        destination.extend(item)
    return destination
