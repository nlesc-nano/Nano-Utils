"""A module for the :class:`DTypeMapping` and :class:`MutableDTypeMapping` classes."""

from __future__ import annotations

import abc
import sys
import copy
import textwrap
import reprlib
from collections.abc import Iterator, KeysView, ValuesView, ItemsView, Callable
from typing import TypeVar, Union, Any, overload, NoReturn, TYPE_CHECKING

if sys.version_info >= (3, 8):
    import functools
    from pprint import pformat as _pformat
    pformat = functools.partial(_pformat, sort_dicts=False)
else:
    from pprint import pformat

if sys.version_info >= (3, 9):
    from collections.abc import Mapping, MutableMapping, Iterable
    from builtins import tuple as Tuple
else:
    from typing import Mapping, MutableMapping, Iterable, Tuple

from .utils import positional_only
from .typing_utils import Protocol, runtime_checkable

_T = TypeVar("_T")
_ST1 = TypeVar("_ST1", bound="UserMapping[Any, Any]")
_ST2 = TypeVar("_ST2", bound="MutableUserMapping[Any, Any]")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_VT_co = TypeVar("_VT_co", covariant=True)

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter

    class _ReprFunc(Protocol[_KT, _VT]):
        def __call__(self, __dct: dict[_KT, _VT], *, width: int) -> str: ...

__all__ = ["UserMapping", "MutableUserMapping", "_DictLike", "_SupportsKeysAndGetItem"]

_SENTINEL = object()


@runtime_checkable
class _SupportsKeysAndGetItem(Protocol[_KT, _VT_co]):
    """A protocol for objects supporting :meth:`~dict.keys` and `~object.__getitem__`."""

    if not TYPE_CHECKING:
        __slots__: str | Iterable[str] = ()

    @abc.abstractmethod
    def keys(self) -> Iterable[_KT]:
        """Return an iterable of keys."""
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, __key: _KT) -> _VT_co:
        """Implement :meth:`self[key] <object.__getitem__>`."""
        raise NotImplementedError


_DictLike = Union[
    _SupportsKeysAndGetItem[_KT, _VT_co],
    Iterable[Tuple[_KT, _VT_co]],
]


def _repr_func(self: UserMapping[_KT, _VT], func: _ReprFunc[_KT, _VT]) -> str:
    """Helper function for :meth:`UserMapping.__repr__`."""
    cls = type(self)
    dict_repr = func(self._dict, width=76)
    if len(dict_repr) <= 76:
        return f"{cls.__name__}({dict_repr})"
    else:
        dict_repr2 = textwrap.indent(dict_repr[1:-1], 3 * " ")
        return f"{cls.__name__}({{\n {dict_repr2},\n}})"


class UserMapping(Mapping[_KT, _VT_co]):
    """Base class for user-defined immutable mappings."""

    __slots__: str | Iterable[str] = ("__weakref__", "_dict", "_hash")

    _dict: dict[_KT, _VT_co]
    _hash: int

    @positional_only
    def __init__(
        self,
        __iterable: None | _DictLike[_KT, _VT_co] = None,
        **kwargs: _VT_co,
    ) -> None:
        """Initialize the instance."""
        if __iterable is None:
            self._dict = kwargs  # type: ignore[assignment]
        else:
            self._dict = dict(__iterable, **kwargs)

    @classmethod
    def _reconstruct(cls: type[_ST1], dct: dict[_KT, _VT_co]) -> _ST1:
        """Alternative constructor without argument validation."""
        self = cls.__new__(cls)
        self._dict = dct
        return self

    def __reduce__(self: _ST1) -> tuple[
        Callable[[dict[_KT, _VT_co]], _ST1],
        tuple[dict[_KT, _VT_co]],
    ]:
        """Helper for :mod:`pickle`."""
        cls = type(self)
        return cls._reconstruct, (self._dict,)

    def copy(self: _ST1) -> _ST1:
        """Return a deep copy of this instance."""
        return copy.deepcopy(self)

    @reprlib.recursive_repr(fillvalue='...')
    def __repr__(self) -> str:
        """Implement :func:`repr(self) <repr>`."""
        return _repr_func(self, func=pformat)

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        """Entry point for the :mod:`IPython <IPython.lib.pretty>` pretty printer."""
        if cycle:
            p.text(f"{type(self).__name__}(...)")
            return None

        from IPython.lib.pretty import pretty
        string = _repr_func(self, func=lambda dct, width: pretty(dct, max_width=width))
        p.text(string)

    def _ipython_key_completions_(self) -> KeysView[_KT]:
        """Entry point for the IPython key completioner."""
        return self.keys()

    def __hash__(self) -> int:
        """Implement :func:`hash(self) <hash>`.

        Raises
        ------
        :exc:`TypeError` : raised when not all values are hashable.

        """
        try:
            return self._hash
        except AttributeError:
            pass
        self._hash = hash(frozenset(self.items()))
        return self._hash

    def __eq__(self, other: object) -> bool:
        """Implement :meth:`self == other <object.__eq__>`."""
        if isinstance(other, UserMapping):
            return self._dict == other._dict
        elif isinstance(other, Mapping):
            return self._dict == other
        else:
            return NotImplemented

    def __getitem__(self, key: _KT) -> _VT_co:
        """Implement :meth:`self[key] <object.__getitem__>`."""
        return self._dict[key]

    def __iter__(self) -> Iterator[_KT]:
        """Implement :func:`iter(self) <iter>`."""
        return iter(self._dict)

    def __len__(self) -> int:
        """Implement :func:`len(self) <len>`."""
        return len(self._dict)

    def __contains__(self, key: object) -> bool:
        """Implement :meth:`key in self <object.__contains__>`."""
        return key in self._dict

    def keys(self) -> KeysView[_KT]:
        """Return a set-like object containing all keys."""
        return self._dict.keys()

    def items(self) -> ItemsView[_KT, _VT_co]:
        """Return a set-like object containing all key/value pairs."""
        return self._dict.items()

    def values(self) -> ValuesView[_VT_co]:
        """Return a collection containing all values."""
        return self._dict.values()

    @overload
    def get(self, key: _KT, default: None = ...) -> _VT_co | None: ...
    @overload
    def get(self, key: _KT, default: _T) -> _VT_co | _T: ...

    def get(self, key, default=None):
        """Return the value for key if the key is present, else default."""
        return self._dict.get(key, default)

    @overload
    @classmethod
    def fromkeys(cls, iterable: Iterable[_T]) -> UserMapping[_T, None]: ...
    @overload
    @classmethod
    def fromkeys(cls, iterable: Iterable[_T], value: _VT) -> UserMapping[_T, _VT]: ...

    @classmethod
    def fromkeys(cls, iterable, value=None):
        """Create a new dictionary with keys from iterable and values set to default."""
        dct = dict.fromkeys(iterable, value)
        return cls._reconstruct(dct)

    if sys.version_info >= (3, 8):
        def __reversed__(self) -> Iterator[_KT]:
            """Implement :func:`reversed(self) <reversed>`."""
            return reversed(self._dict)

    if sys.version_info >= (3, 9):
        def __or__(self: _ST1, other: Mapping[_KT, _VT_co]) -> _ST1:
            """Implement :meth:`self | other <object.__or__>`."""
            cls = type(self)
            if not isinstance(other, Mapping):
                return NotImplemented
            elif isinstance(other, UserMapping):
                return cls._reconstruct(self._dict | other._dict)
            else:
                return cls._reconstruct(self._dict | other)

        def __ror__(self: _ST1, other: Mapping[_KT, _VT_co]) -> _ST1:
            """Implement :meth:`other | self <object.__ror__>`."""
            cls = type(self)
            if not isinstance(other, Mapping):
                return NotImplemented
            elif isinstance(other, UserMapping):
                return cls._reconstruct(other._dict | self._dict)
            else:
                return cls._reconstruct(other | self._dict)

        if not TYPE_CHECKING:
            def __ior__(self, other: Mapping[_KT, _VT_co]) -> NoReturn:
                """Implement :meth:`self |= other <object.__ior__>`.

                Warning
                -------
                Unsupported operation.

                """
                cls = type(self)
                raise TypeError(f"'|=' is not supported by {cls.__name__!r}; use '|' instead")


class MutableUserMapping(UserMapping[_KT, _VT], MutableMapping[_KT, _VT]):
    """Base class for user-defined mutable mappings."""

    __slots__: str | Iterable[str] = ()
    __hash__ = None  # type: ignore[assignment]

    def __copy__(self: _ST2) -> _ST2:
        """Implement :func:`copy.copy(self) <copy.copy>`."""
        return copy.deepcopy(self)

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """Implement :meth:`self[key] = value <object.__setitem__>`."""
        self._dict[key] = value

    def __delitem__(self, key: _KT) -> None:
        """Implement :meth:`del self[key] <object.__delitem__>`."""
        del self._dict[key]

    def clear(self) -> None:
        """Remove all items from the mapping."""
        return self._dict.clear()

    def popitem(self) -> tuple[_KT, _VT]:
        """Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO (last-in, first-out) order.
        Raises a :exc:`KeyError` if the mapping is empty.
        """
        return self._dict.popitem()

    @overload
    def pop(self, key: _KT) -> _VT: ...
    @overload
    def pop(self, key: _KT, default: _T = ...) -> _VT | _T: ...

    def pop(self, key, default=_SENTINEL):
        """Remove the specified key and return the corresponding value.

        If the key is not found, default is returned if given,
        otherwise a :exc:`KeyError` is raised.
        """
        if default is _SENTINEL:
            return self._dict.pop(key)
        else:
            return self._dict.pop(key, default)

    @positional_only
    def update(self, __iterable: None | _DictLike[_KT, _VT] = None, **kwargs: _VT) -> None:
        """Update the mapping from the passed mapping or iterable."""
        if __iterable is None:
            self._dict.update(**kwargs)
        else:
            self._dict.update(__iterable, **kwargs)

    if sys.version_info >= (3, 9):
        def __ior__(self: _ST2, other: Mapping[_KT, _VT]) -> _ST2:
            """Implement :meth:`self |= other <object.__ior__>`."""
            if not isinstance(other, Mapping):
                return NotImplemented
            elif isinstance(other, UserMapping):
                self._dict |= other._dict
            else:
                self._dict |= other
            return self

    if TYPE_CHECKING:
        @overload  # type: ignore
        @classmethod
        def fromkeys(cls, iterable: Iterable[_T]) -> MutableUserMapping[_T, None | Any]: ...
        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[_T], value: _VT) -> MutableUserMapping[_T, _VT]: ...
