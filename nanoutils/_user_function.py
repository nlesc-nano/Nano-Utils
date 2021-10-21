from __future__ import annotations

import sys
import types
import inspect
import reprlib
from typing import Generic, TypeVar, Any, TYPE_CHECKING, Callable

__all__ = ["UserFunctionType"]

_T = TypeVar("_T")
_FT = TypeVar("_FT", bound=Callable[..., Any])


def _is_pickleable(func: object) -> bool:
    return hasattr(func, "__qualname__") and hasattr(func, "__module__")


class UserFunctionType(Generic[_FT]):
    """A baseclass for function-wrappers with extra attributes.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import UserFunctionType
        >>> import numpy as np

        >>> class SumFunction(UserFunctionType):
        ...     def sum(start, stop, step=None, *, axis=None):
        ...         return self(start, stop, step).sum(axis=axis)
        ...

        >>> @SumFunction
        ... def get_range(start, stop, step=None):
        ...     return np.arange(start, stop, step=step)

        >>> get_range(5, 10)
        array([5, 6, 7, 8, 9])

        >>> get_range.sum(5, 10)
        35

    """

    __slots__ = ("__weakref__", "__call__", "__dict__")

    __call__: _FT
    __doc__: None | str
    __module__: str
    __annotations__: dict[str, Any]

    def __init__(self, func: _FT) -> None:
        """Initialize the instance."""
        if not callable(func):
            raise TypeError("`func` expected a function")

        self.__call__ = func
        self.__doc__ = getattr(func, "__doc__", None)
        self.__annotations__ = getattr(func, "__annotations__", {})
        self.__module__ = getattr(func, "__module__", "__main__")

    def __dir__(self) -> list[str]:
        """Implement :func:`dir(self) <dir>`."""
        dir_set = set(super().__dir__())
        dir_set.update(dir(self.__call__))
        return sorted(dir_set)

    @reprlib.recursive_repr("...")
    def __repr__(self) -> str:
        """Implement :func:`repr(self) <repr>`."""
        func = self.__call__
        try:
            sgn: str | inspect.Signature = inspect.signature(func)
        except ValueError:
            sgn = "(...)"

        name_list = []
        if hasattr(func, "__module__"):
            name_list.append(func.__module__)
        if hasattr(func, "__qualname__"):
            name_list.append(func.__qualname__)
        elif hasattr(func, "__name__"):
            name_list.append(func.__name__)
        else:
            return f"<{type(self).__name__} instance {func!r}>"
        return f"<{type(self).__name__} instance {'.'.join(name_list)}{sgn}>"

    def __reduce__(self) -> str:
        """Helper method for :mod:`pickle`."""
        if _is_pickleable(self.__call__):
            return self.__qualname__
        else:
            raise TypeError(f"Cannot pickle {self!r}")

    def __copy__(self: _T) -> _T:
        """Implement :func:`copy.copy(self) <copy.copy>`."""
        return self

    def __deepcopy__(self: _T, memo: object = None) -> _T:
        """Implement :func:`copy.deepcopy(self, memo=memo) <copy.deepcopy>`."""
        return self

    def __get__(self, instance: Any, cls: type | None = None) -> types.MethodType:
        """Implement :meth:`~object.__get__`."""
        if cls is not None:
            return types.MethodType(self, cls)
        else:
            return types.MethodType(self, instance)

    # Provide read-only views of all attributes of the underlying function
    if not TYPE_CHECKING:
        def __getattr__(self, name: str) -> Any:
            """Implement :func:`getattr(self, name) <getattr>`."""
            try:
                return getattr(self.__call__, name)
            except AttributeError:
                pass
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

        def __setattr__(self, name: str, value: Any) -> None:
            """Implement :func:`setattr(self, name, value) <setattr>`."""
            try:
                return super().__setattr__(name, value)
            except AttributeError:
                if not hasattr(self, name):
                    raise
            raise AttributeError(f"{type(self).__name__!r} object attribute {name!r} is read-only")

        def __delattr__(self, name: str) -> None:
            """Implement :func:`delattr(self, name) <delattr>`."""
            try:
                return super().__delattr__(name)
            except AttributeError:
                if not hasattr(self, name):
                    raise
            raise AttributeError(f"{type(self).__name__!r} object attribute {name!r} is read-only")

    # NOTE: We're assuming here that the callable is a `types.FunctionType` instance
    else:
        @property
        def __closure__(self) -> tuple[types._Cell, ...] | None: ...
        @property
        def __code__(self) -> types.CodeType: ...
        @property
        def __defaults__(self) -> tuple[Any, ...] | None: ...
        @property
        def __globals__(self) -> dict[str, Any]: ...
        @property
        def __name__(self) -> str: ...
        @property
        def __qualname__(self) -> str: ...
        @property
        def __kwdefaults__(self) -> dict[str, Any]: ...
