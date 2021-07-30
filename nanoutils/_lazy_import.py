"""A private module for containg the :class:`LazyImporter` and :class:`MutableLazyImporter` classes.

Notes
-----
:class:`~nanoutils.LazyImporter` and :class:`~nanoutils.MutableLazyImporter`
should be imported from either :mod:`nanoutils` or :mod:`nanoutils.utils`.

"""  # noqa: E501

from __future__ import annotations

import sys
import types
import reprlib
import importlib
from collections.abc import Mapping, Callable, Iterable
from typing import Any, TypeVar, Type, Generic, cast, TYPE_CHECKING

_T = TypeVar("_T")

if TYPE_CHECKING:
    from typing_extensions import Protocol
    from typing import (
        overload,
        Collection,
        Union,
        Tuple,
        Dict,
        KeysView,
        ValuesView,
        ItemsView,
        Iterator,
    )

    _KT = TypeVar("_KT")
    _VT = TypeVar("_VT")
    _VT_co = TypeVar("_VT_co", covariant=True)
    _ST1 = TypeVar("_ST1", bound="LazyImporter[Any]")
    _ST2 = TypeVar("_ST2", bound="MutableLazyImporter[Any]")

    class _SupportsKeysAndGetItem(Protocol[_KT, _VT_co]):
        def __getitem__(self, __key: _KT) -> _VT_co: ...
        def keys(self) -> Iterable[_KT]: ...

    # A `Protocol` version of `types.MappingProxyType`
    class _MappingProtocol(Protocol[_KT, _VT], Collection[_KT]):
        __hash__: None  # type: ignore
        def __getitem__(self, k: _KT) -> _VT: ...
        def __contains__(self, o: object) -> bool: ...
        @overload
        def get(self, key: _KT) -> None | _VT: ...
        @overload
        def get(self, key: _KT, default: _T) -> _T | _VT: ...
        def items(self) -> ItemsView[_KT, _VT]: ...
        def keys(self) -> KeysView[_KT]: ...
        def values(self) -> ValuesView[_VT]: ...
        def copy(self) -> dict[_KT, _VT]: ...

        # TODO: Update `__or__` once mypy > 0.910 hits
        if sys.version_info >= (3, 9):
            def __reversed__(self) -> Iterator[_KT]: ...
            def __or__(self, __value: Mapping[_KT, _VT]) -> dict[_KT, _VT]: ...
            def __ror__(self, __value: Mapping[_KT, _VT]) -> dict[_KT, _VT]: ...

    _DictLike = Union[_SupportsKeysAndGetItem[str, str], Iterable[Tuple[str, str]]]
    _ReduceTuple = Tuple[Callable[[str, Dict[str, str]], _T], Tuple[str, Dict[str, str]]]

__all__ = ["MutableLazyImporter", "LazyImporter"]


class _CustomRepr(reprlib.Repr):
    def __init__(self) -> None:
        super().__init__()
        self.maxdict = 2

    def repr_mappingproxy(self, x, level):
        return self.repr_dict(x, level)


_repr = _CustomRepr().repr


class LazyImporter(Generic[_T]):
    """A class for lazilly importing objects.

    Parameters
    ----------
    module : :class:`types.ModuleType`
        The to-be wrapped module.
    imports : :class:`Mapping[str, str]<collections.abc.Mapping>`
        A mapping that maps the names of to-be lazzily imported objects
        to the names of their modules.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import LazyImporter

        >>> __getattr__ = LazyImporter.from_name("nanoutils", {"Any": "typing"})
        >>> print(__getattr__)
        LazyImporter(module=nanoutils, imports={'Any': 'typing'})

        >>> __getattr__("Any")
        typing.Any

    """

    __slots__ = ("__weakref__", "_imports", "_module", "_hash")

    @property
    def module(self) -> types.ModuleType:
        """:class:`types.ModuleType`: Get the wrapped module."""
        return self._module

    @property
    def imports(self) -> _MappingProtocol[str, str]:
        """:class:`types.MappingProxyType[str, str]<types.MappingProxyType>`: Get a mapping that maps object names to their module name."""  # noqa: E501
        return self._imports

    def __init__(
        self: LazyImporter[Any],
        module: types.ModuleType,
        imports: _DictLike,
    ) -> None:
        """Initialize a new instance."""
        if not isinstance(module, types.ModuleType):
            raise TypeError(f"Expected a module, not {type(module).__name__}")
        self._module = module
        self._imports = cast("_MappingProtocol[str, str]", types.MappingProxyType(dict(imports)))

    @classmethod
    def from_name(cls: Type[_ST1], name: str, imports: _DictLike) -> _ST1:
        """Construct a new instance from the module **name**.

        Parameters
        ----------
        name : :class:`str`
            The name of the to-be wrapped module.
        imports : :class:`Mapping[str, str]<collections.abc.Mapping>`
            A mapping that maps the names of to-be lazzily imported objects
            to the names of their modules.

        Returns
        -------
        :class:`nanoutils.LazyImporter`
            A new LazyImporter instance or a subclass thereof.

        """
        if not isinstance(name, str):
            raise TypeError(f"Expected a string, not {type(name).__name__}")

        module = sys.modules.get(name)  # fast-path
        if module is None:
            module = importlib.import_module(name)
        return cls(module, imports)

    def __reduce__(self: _ST1) -> _ReduceTuple[_ST1]:
        """Helper for :mod:`pickle`."""
        cls = type(self)
        args = (self.module.__name__, self.imports.copy())
        return cls.from_name, args

    def __copy__(self: _ST1) -> _ST1:
        """Implement :func:`copy.copy(self)<copy.copy>`."""
        return self

    def __deepcopy__(self: _ST1, memo: None | dict[int, Any] = None) -> _ST1:
        """Implement :func:`copy.deepcopy(self, memo=memo)<copy.deepcopy>`."""
        return self

    def __hash__(self) -> int:
        """Implement :func:`hash(self)<hash>`."""
        try:
            return self._hash
        except AttributeError:
            self._hash: int = hash(self._module) ^ hash(frozenset(self.imports.items()))
            return self._hash

    def __eq__(self, value: object) -> bool:
        """Implement :meth:`self == value<object.__eq__>`."""
        cls = type(self)
        if not isinstance(value, cls):
            return NotImplemented
        return self.module is value.module and self.imports == value.imports

    def __repr__(self) -> str:
        """Implement :func:`repr(self)<repr>`."""
        name = type(self).__name__
        return f"{name}(module={self.module.__name__}, imports={_repr(self.imports)})"

    def __call__(self, name: str) -> _T:
        """Implement :func:`getattr(self.module, name)<getattr>`."""
        # Get the module-name associated with `name`
        try:
            module_name = self.imports[name]
        except KeyError:
            raise AttributeError(
                f"module {self.module.__name__!r} has no attribute {name!r}"
            ) from None

        # Import the module
        module = sys.modules.get(module_name)
        if module is None:
            module = importlib.import_module(module_name)

        # Extract `name` from `module`
        ret: _T = getattr(module, name)
        setattr(self.module, name, ret)
        return ret


class MutableLazyImporter(LazyImporter[_T]):
    """A subclass of :class:`~nanoutils.LazyImporter` with mutable :attr:`imports`.

    Parameters
    ----------
    module : :class:`types.ModuleType`
        The to-be wrapped module.
    imports : :class:`Mapping[str, str]<collections.abc.Mapping>`
        A mapping that maps the names of to-be lazzily imported objects
        to the names of their modules.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import MutableLazyImporter

        >>> __getattr__ = MutableLazyImporter.from_name("nanoutils", {"Any": "typing"})
        >>> print(__getattr__)
        MutableLazyImporter(module=nanoutils, imports={'Any': 'typing'})

        >>> __getattr__("Any")
        typing.Any

        >>> del __getattr__.imports["Any"]
        >>> print(__getattr__)
        MutableLazyImporter(module=nanoutils, imports={})

        >>> __getattr__.imports = {"Hashable": "collections.abc"}
        >>> __getattr__("Hashable")
        <class 'collections.abc.Hashable'>

    """

    __hash__ = None  # type: ignore[assignment]

    @property
    def imports(self) -> dict[str, str]:
        """:class:`dict[str, str]<dict>`: Get or set the dictionary that maps object names to their module name.

        Setting a value will assign it as a copy.

        """  # noqa: E501
        return self._imports

    @imports.setter
    def imports(self, value: _DictLike) -> None:
        self._imports = dict(value)

    def __init__(
        self: MutableLazyImporter[Any],
        module: types.ModuleType,
        imports: _DictLike,
    ) -> None:
        """Initialize a :class:`MutableLazyImporter` instance."""
        if not isinstance(module, types.ModuleType):
            raise TypeError(f"Expected a module, not {module.__class__.__name__}")
        self._module = module
        self._imports: dict[str, str] = dict(imports)

    def __copy__(self: _ST2) -> _ST2:
        """Implement :func:`copy.copy(self)<copy.copy>`."""
        cls = type(self)
        ret: _ST2 = object.__new__(cls)
        ret._module = self.module
        ret._imports = self.imports
        return ret

    def __deepcopy__(self: _ST2, memo: None | dict[int, Any] = None) -> _ST2:
        """Implement :func:`copy.deepcopy(self, memo=memo)<copy.deepcopy>`."""
        cls = type(self)
        ret: _ST2 = object.__new__(cls)
        ret._module = self.module
        ret._imports = self.imports.copy()
        return ret

    def __reduce__(self: _ST2) -> _ReduceTuple[_ST2]:
        """Helper for :mod:`pickle`."""
        cls = type(self)
        return cls.from_name, (self.module.__name__, self.imports)
