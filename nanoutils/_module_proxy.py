from __future__ import annotations

import sys
import types
import functools
from collections.abc import Iterable
from typing import Any, Generic, TypeVar, ClassVar

__all__ = ["ModuleProxy"]

_T = TypeVar("_T")
_Self = TypeVar("_Self", bound="ModuleProxyBase[Any]")


class ModuleProxyBase(Generic[_T]):
    __slots__ = ("__weakref__", "_obj")

    MODULE: ClassVar[types.ModuleType] = sys.modules["__main__"]
    ATTR: ClassVar[frozenset[str]] = frozenset({})

    @property
    def __self__(self) -> _T:
        return self._obj

    def __init__(self, obj: _T, /) -> None:
        self._obj = obj

    def __hash__(self) -> int:
        return id(self._obj)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self._obj is other._obj

    def __reduce__(self: _Self) -> tuple[type[_Self], tuple[_T]]:
        cls = type(self)
        return cls, (self._obj,)

    def __repr__(self) -> str:
        wrapper_name = type(self).MODULE.__name__
        obj_cls = type(self._obj)
        obj_name = f"{obj_cls.__module__}.{obj_cls.__name__} object"
        return f"<bound {wrapper_name} wrapper of {obj_name}>"

    def __init_subclass__(
        cls,
        *,
        MODULE: None | types.ModuleType = None,
        ATTR: None | Iterable[str] = None,
    ) -> None:
        module = MODULE if MODULE is not None else getattr(cls, "MODULE")
        attr = ATTR if ATTR is not None else getattr(cls, "ATTR")

        # Validate argument types
        if not isinstance(module, types.ModuleType):
            raise TypeError(f"{type(module).__name__!r} object is not a module")

        cls.MODULE = module
        cls.ATTR = frozenset(attr)

        # Assign methods
        for name in cls.ATTR:
            if hasattr(cls, name) and (ATTR is MODULE is None):
                continue

            func = getattr(module, name)
            if func is getattr(cls, "__wrapped__", None):
                continue

            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                return func(self._obj, *args, **kwargs)

            setattr(cls, name, wrapper)
        return super().__init_subclass__()
