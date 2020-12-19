__all__ = ["copy_func"]


# standard library
from copy import copy, deepcopy
from types import FunctionType
from typing import Callable


# main features
def copy_func(func: Callable, deep: bool = False) -> Callable:
    """Copy a function as a different object.

    Args:
        func: A function object to be copied.
        deep: If ``True``, mutable attributes of ``func`` are deep-copied.

    Returns:
        A function as a different object from the original one.

    """
    copied = FunctionType(
        func.__code__,
        func.__globals__,
        func.__name__,
        func.__defaults__,
        func.__closure__,
    )

    # mutable attributes are copied by the given method
    copier = deepcopy if deep else copy
    copied.__annotations__ = copier(func.__annotations__)
    copied.__dict__ = copier(func.__dict__)
    copied.__kwdefaults__ = copier(func.__kwdefaults__)

    # immutable attributes are not copied (just assigned)
    copied.__doc__ = func.__doc__
    copied.__module__ = func.__module__
    copied.__name__ = func.__name__
    copied.__qualname__ = func.__qualname__

    return copied
