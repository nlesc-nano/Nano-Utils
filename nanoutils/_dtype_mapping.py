"""A module for the :class:`DTypeMapping` and :class:`MutableDTypeMapping` classes."""

from __future__ import annotations

import sys
from collections.abc import Iterable, Iterator, Callable, Mapping
from typing import TypeVar, TYPE_CHECKING, Any, ClassVar

from .numpy_utils import NUMPY_EX
from .utils import raise_if, positional_only
from ._user_dict import _DictLike, UserMapping, MutableUserMapping, _SupportsKeysAndGetItem

if TYPE_CHECKING or NUMPY_EX is None:
    import numpy as np
    from numpy import dtype
else:
    dtype = "numpy.dtype"

if TYPE_CHECKING:
    import numpy.typing as npt
    from IPython.lib.pretty import RepresentationPrinter
    from typing_extensions import TypeGuard

__all__ = ["DTypeMapping", "MutableDTypeMapping"]

_T = TypeVar("_T")
_ST1 = TypeVar("_ST1", bound="DTypeMapping")
_ST2 = TypeVar("_ST2", bound="MutableDTypeMapping")


def _has_keys(obj: object) -> TypeGuard[_SupportsKeysAndGetItem[Any, Any]]:
    """Check if the passed obj has the :meth:`~dict.keys` method."""
    return callable(getattr(obj, "keys", None))


def _repr_helper(self: DTypeMapping, dtype_repr: Callable[[np.dtype[Any]], str]) -> str:
    """Helper function for :meth:`DTypeMapping.__repr__`."""
    cls = type(self)
    if len(self) == 0:
        return f"{cls.__name__}()"

    offset = max([len(i) for i in self], default=0)
    values = "\n".join(f"    {k:{offset}} = {dtype_repr(v)}," for k, v in self.items())
    return f"{cls.__name__}(\n{values}\n)"


class DTypeMapping(UserMapping[str, "dtype[Any]"]):
    """A mapping for creating structured dtypes.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import DTypeMapping
        >>> import numpy as np

        >>> DType1 = DTypeMapping({"x": float, "y": float, "z": float, "symbol": (str, 2)})
        >>> print(DType1)
        DTypeMapping(
            x      = float64,
            y      = float64,
            z      = float64,
            symbol = <U2,
        )

        >>> DType1.x
        dtype('float64')

        >>> DType1.symbol
        dtype('<U2')

        >>> @DTypeMapping.from_type
        ... class DType2:
        ...     xyz = (float, 3)
        ...     symbol = (str, 2)
        ...     charge = np.int64

        >>> print(DType2)
        DTypeMapping(
            xyz    = ('<f8', (3,)),
            symbol = <U2,
            charge = int64,
        )

    """

    __slots__ = ("_dtype",)
    _SLOTS: ClassVar[frozenset[str]] = frozenset({"__weakref__", "_hash", "_dtype", "_dict"})

    @property
    def dtype(self) -> np.dtype[np.void]:
        """Get a structured dtype constructed from dtype mapping."""
        try:
            return self._dtype
        except AttributeError:
            pass
        self._dtype: np.dtype[np.void] = np.dtype(list(self.items()))
        return self._dtype

    @raise_if(NUMPY_EX)
    @positional_only
    def __init__(
        self,
        __iterable: None | _DictLike[str, npt.DTypeLike] = None,
        **fields: npt.DTypeLike,
    ) -> None:
        """Initialize the instance."""
        if __iterable is None:
            dct = {}
        elif _has_keys(__iterable):
            dct = {k: np.dtype(__iterable[k]) for k in __iterable.keys()}
        else:
            dct = {k: np.dtype(v) for k, v in __iterable}  # type: ignore[union-attr]
        dct.update({k: np.dtype(v) for k, v in fields.items()})
        super().__setattr__("_dict", dct)

    @classmethod
    @raise_if(NUMPY_EX)
    def from_type(cls: type[_ST1], type_obj: type) -> _ST1:
        """Construct a new dtype mapping from all public attributes of the decorated type object.

        Example
        -------
        .. code-block:: python

            >>> from nanoutils import DTypeMapping

            >>> @DTypeMapping.from_type
            ... class AtomsDType:
            ...     xyz = (float, 3)
            ...     symbol = (str, 2)
            ...     charge = np.int64

            >>> print(AtomsDType)
            DTypeMapping(
                xyz    = ('<f8', (3,)),
                symbol = <U2,
                charge = int64,
            )

        Parameters
        ----------
        type_obj : :class:`type`
            A type object or any object that supports :func:`vars`.

        """
        try:
            dct = vars(type_obj)
        except TypeError:
            raise TypeError(f"Expected a type object, got {type(type_obj).__name__!r}") from None
        return cls._reconstruct({k: np.dtype(v) for k, v in dct.items() if not k.startswith("_")})

    def __repr__(self) -> str:
        """Implement :func:`repr(self) <repr>`."""
        return _repr_helper(self, lambda dtype: f"numpy.{dtype!r}")

    def __str__(self) -> str:
        """Implement :class:`str(self) <str>`."""
        return _repr_helper(self, str)

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        """Entry point for the :mod:`IPython <IPython.lib.pretty>` pretty printer."""
        if cycle:
            cls = type(self)
            p.text(f"{cls.__name__}(...)")
        else:
            p.text(str(self))

    def __hash__(self) -> int:
        """Implement :func:`hash(self) <hash>`."""
        try:
            return self._hash
        except AttributeError:
            pass
        self._hash = hash(tuple(self.items()))
        return self._hash

    def __eq__(self, other: object) -> bool:
        """Implement :meth:`self == other <object.__eq__>`."""
        if not isinstance(other, DTypeMapping):
            return NotImplemented
        iterator = zip(self._dict.items(), other._dict.items())
        return all(i == j for i, j in iterator)

    @classmethod
    @raise_if(NUMPY_EX)
    def fromkeys(  # type: ignore[override]
        cls: type[_ST1],
        iterable: Iterable[str],
        value: npt.DTypeLike = None,
    ) -> _ST1:
        """Create a new dictionary with keys from iterable and values set to value."""
        value = np.dtype(value)
        dct = dict.fromkeys(iterable, value)
        return cls._reconstruct(dct)

    def __getattr__(self, name: str) -> np.dtype[Any]:
        """Implement :func:`getattr(self, name) <getattr>`."""
        try:
            return self[name]
        except KeyError:
            cls = type(self)
            raise AttributeError(f"{cls.__name__!r} object has no attribute {name!r}") from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Implement :func:`setattr(self, name, value) <setattr>`."""
        cls = type(self)
        if name not in cls._SLOTS and name in self:
            raise AttributeError(f"{cls.__name__!r} object attribute {name!r} is read-only")
        return super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """Implement :func:`delattr(self, name) <delattr>`."""
        cls = type(self)
        if name not in cls._SLOTS and name in self:
            raise AttributeError(f"{cls.__name__!r} object attribute {name!r} is read-only")
        return super().__delattr__(name)

    def __dir__(self) -> list[str]:
        """Implement :func:`dir(self) <dir>`."""
        return sorted(set(super().__dir__()) | self.keys())

    if sys.version_info < (3, 8):
        def __reversed__(self) -> Iterator[str]:
            """Implement :func:`reversed(self) <reversed>`."""
            return reversed(list(self))

    if sys.version_info >= (3, 9):
        def __or__(self: _ST1, other: Mapping[str, npt.DTypeLike]) -> _ST1:
            """Implement :meth:`self | other <object.__or__>`."""
            if not isinstance(other, Mapping):
                return NotImplemented

            cls = type(self)
            if isinstance(other, DTypeMapping):
                return cls._reconstruct(self._dict | other._dict)
            else:
                return cls._reconstruct(self._dict | {k: np.dtype(v) for k, v in other.items()})

        def __ror__(self: _ST1, other: Mapping[str, npt.DTypeLike]) -> _ST1:
            """Implement :meth:`other | self <object.__ror__>`."""
            if not isinstance(other, Mapping):
                return NotImplemented

            cls = type(self)
            if isinstance(other, DTypeMapping):
                return cls._reconstruct(other._dict | self._dict)
            else:
                return cls._reconstruct({k: np.dtype(v) for k, v in other.items()} | self._dict)


class MutableDTypeMapping(  # type: ignore[misc]
    DTypeMapping,
    MutableUserMapping[str, "dtype[Any]"],
):
    """A mutable mapping for creating structured dtypes.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import DTypeMapping
        >>> import numpy as np

        >>> DType1 = MutableDTypeMapping({"x": float, "y": float, "z": float, "symbol": (str, 2)})
        >>> print(DType1)
        MutableDTypeMapping(
            x      = float64,
            y      = float64,
            z      = float64,
            symbol = <U2,
        )

        >>> @MutableDTypeMapping.from_type
        ... class DType2:
        ...     xyz = (float, 3)
        ...     symbol = (str, 2)
        ...     charge = np.int64

        >>> print(DType2)
        MutableDTypeMapping(
            xyz    = ('<f8', (3,)),
            symbol = <U2,
            charge = int64,
        )

    """

    __slots__ = ()
    __hash__ = None  # type: ignore[assignment]

    @property
    def dtype(self) -> np.dtype[np.void]:
        """Get a structured dtype constructed from the mapping."""
        return np.dtype(list(self.items()))

    def __setitem__(self, key: str, value: npt.DTypeLike) -> None:
        """Implement :meth:`self[key] = value <object.__setitem__>`."""
        self._dict[key] = np.dtype(value)

    def __setattr__(self, name: str, value: npt.DTypeLike) -> None:
        """Implement :func:`setattr(self, name, value) <setattr>`."""
        cls = type(self)
        if name not in cls._SLOTS and name in self:
            self[name] = value
        else:
            return object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        """Implement :func:`delattr(self, name) <delattr>`."""
        cls = type(self)
        if name not in cls._SLOTS and name in self:
            del self[name]
        else:
            return object.__delattr__(self, name)

    @positional_only
    def update(
        self,
        __iterable: None | _DictLike[str, npt.DTypeLike] = None,
        **fields: npt.DTypeLike,
    ) -> None:
        """Update the mapping from the passed mapping or iterable."""
        if __iterable is None:
            pass
        elif _has_keys(__iterable):
            self._dict.update({k: np.dtype(__iterable[k]) for k in __iterable.keys()})
        else:
            self._dict.update({k: np.dtype(v) for k, v in __iterable})  # type: ignore[union-attr]
        self._dict.update({k: np.dtype(v) for k, v in fields.items()})

    if sys.version_info >= (3, 9):
        def __ior__(self: _ST2, other: Mapping[str, npt.DTypeLike]) -> _ST2:
            """Implement :meth:`self |= other <object.__ior__>`."""
            if not isinstance(other, Mapping):
                return NotImplemented
            elif isinstance(other, DTypeMapping):
                self._dict |= other._dict
            else:
                self._dict |= {k: np.dtype(v) for k, v in other.items()}
            return self
