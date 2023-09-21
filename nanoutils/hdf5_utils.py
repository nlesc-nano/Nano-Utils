"""An module with various :mod:`h5py`-related utilities.

Index
-----
.. currentmodule:: nanoutils
.. autosummary::
    RecursiveKeysView
    RecursiveValuesView
    RecursiveItemsView

API
---
.. autoclass:: RecursiveKeysView
.. autoclass:: RecursiveValuesView
.. autoclass:: RecursiveItemsView

"""

from __future__ import annotations

import sys
import abc
from collections import Counter
from collections.abc import Generator, MappingView, Iterator, Iterable, Set as AbstractSet
from typing import NoReturn, ClassVar, Any, TypeVar, Generic, TYPE_CHECKING
from packaging.version import Version

if sys.version_info >= (3, 9):
    from collections.abc import KeysView, ValuesView, ItemsView
    from builtins import tuple as Tuple
else:
    from typing import KeysView, ValuesView, ItemsView, Tuple

from .utils import raise_if, construct_api_doc

try:
    import h5py
    from h5py import Dataset as H5PyDataset
    H5PY_EX: None | Exception = None
    H5PY_VERSION = Version(h5py.__version__)
except Exception as ex:
    if not TYPE_CHECKING:
        H5PY_EX = ex
        H5PY_VERSION = Version("0.0.0")
        H5PyDataset = "h5py.Dataset"

_T_co = TypeVar("_T_co", covariant=True)
_T = TypeVar("_T")

__all__ = [
    'recursive_keys',
    'recursive_values',
    'recursive_items',
    'RecursiveKeysView',
    'RecursiveValuesView',
    'RecursiveItemsView',
]


class _Mixin(Generic[_T_co]):
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self) == self._from_iterable(other)

    def __le__(self, other: AbstractSet[Any]) -> bool:
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self).issubset(other)

    def __ge__(self, other: AbstractSet[Any]) -> bool:
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self).issuperset(other)

    def __or__(self, other: AbstractSet[_T]) -> set[_T_co | _T]:
        """Implement :code:`self | other`."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self).union(other)

    def __xor__(self, other: AbstractSet[_T]) -> set[_T_co | _T]:
        """Implement :code:`self ^ other`."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self).symmetric_difference(other)  # type: ignore

    def __and__(self, other: AbstractSet[Any]) -> set[_T_co]:
        """Implement :code:`self & other`."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self).intersection(other)

    def __sub__(self, other: AbstractSet[Any]) -> set[_T_co]:
        """Implement :code:`self - other`."""
        if not isinstance(other, AbstractSet):
            return NotImplemented
        return self._from_iterable(self).difference(other)

    if TYPE_CHECKING:
        @abc.abstractmethod
        def __iter__(self) -> Iterator[_T_co]: ...

        @classmethod
        def _from_iterable(cls, it: Iterable[_T_co]) -> set[_T_co]: ...
    else:
        __rand__ = __and__
        __ror__ = __or__
        __rxor__ = __xor__

        def __rsub__(self, other: AbstractSet[_T]) -> set[_T]:
            """Implement :code:`other - self`."""
            if not isinstance(other, AbstractSet):
                return NotImplemented
            return self._from_iterable(other).difference(self)


class _RecursiveMappingView(MappingView, metaclass=abc.ABCMeta):
    """Base class for recursive group or file views."""

    __slots__ = ("__weakref__",)

    _mapping: h5py.Group
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @raise_if(H5PY_EX)
    def __init__(self, f: h5py.Group) -> None:
        if not isinstance(f, h5py.Group):
            raise TypeError("Expected a h5py Group or File")
        super().__init__(f)

    @property
    def mapping(self) -> h5py.Group:
        """:class:`h5py.Group`: Get the underlying mapping."""
        return self._mapping

    @classmethod
    def _iter_dfs(
        cls,
        group: h5py.Group,
        reverse: bool = False,
    ) -> Generator[tuple[str, h5py.Dataset], None, None]:
        """Recursively iterate through **group** in depth-first order."""
        iterable = group.values() if not reverse else reversed(group.values())
        for v in iterable:
            if isinstance(v, h5py.Group):
                yield from cls._iter_dfs(v, reverse)
            else:
                yield v.name, v

    def __repr__(self) -> str:
        """Implement :func:`repr(self) <repr>`."""
        cls = type(self)
        indent = " " * (3 + len(cls.__name__))
        data = f",\n{indent}".join(repr(i) for i in self)
        return f"<{cls.__name__} [{data}]>"

    def __len__(self) -> int:
        """Implement :func:`len(self)<len>`."""
        i = 0
        for i, _ in enumerate(self, 1):
            pass
        return i

    def __contains__(self, key: object) -> bool:
        """Implement :meth:`key in self<object.__contains__>`."""
        return any((key == i) for i in self)

    @abc.abstractmethod
    def __iter__(self) -> Iterator[object]:
        """Implement :func:`iter(self)<iter>`."""
        raise NotImplementedError("Trying to call an abstract method")

    if TYPE_CHECKING or H5PY_VERSION >= Version("3.5.0"):
        @abc.abstractmethod
        def __reversed__(self) -> Iterator[object]:
            """Implement :func:`reversed(self)<reversed>`.

            Note
            ----
            This feature requires h5py >= 3.5.

            """
            raise NotImplementedError("Trying to call an abstract method")
    else:
        def __reversed__(self) -> NoReturn:
            """Implement :func:`reversed(self)<reversed>`.

            Warning
            -------
            This feature requires h5py >= 3.5.

            """
            raise TypeError("`reversed` requires h5py >= 3.5.0") from H5PY_EX


class RecursiveKeysView(_Mixin[str], _RecursiveMappingView, KeysView[str]):  # type: ignore[misc]
    """Create a recursive view of all dataset :attr:`names<h5py.Dataset.name>`.

    Examples
    --------
    .. testsetup:: python

        >>> import os
        >>> filename = os.path.join('tests', 'test_files', '_test.hdf5')
        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    .. doctest:: python
        :skipif: HDF5_EX is not None

        >>> import h5py
        >>> from nanoutils import RecursiveKeysView

        >>> filename: str = ...  # doctest: +SKIP

        >>> with h5py.File(filename, 'a') as f:
        ...     a = f.create_group('a')
        ...     b = f['a'].create_group('b')
        ...
        ...     dset1 = f.create_dataset('dset1', (10,), dtype=float)
        ...     dset2 = f['a'].create_dataset('dset2', (10,), dtype=float)
        ...     dset3 = f['a']['b'].create_dataset('dset3', (10,), dtype=float)
        ...
        ...     print(RecursiveKeysView(f))
        <RecursiveKeysView ['/a/b/dset3',
                            '/a/dset2',
                            '/dset1']>

    .. testcleanup:: python

        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    Parameters
    ----------
    f : :class:`h5py.Group`
        The to-be iterated h5py group of file.

    Returns
    -------
    :class:`KeysView[str]<collections.abc.KeysView>`
        A recursive view of all dataset names within the passed group or file.

    """

    __slots__ = ()

    def __iter__(self) -> Generator[str, None, None]:
        """Implement :func:`iter(self)<iter>`."""
        for k, _ in self._iter_dfs(self._mapping):
            yield k

    if TYPE_CHECKING or H5PY_VERSION >= Version("3.5.0"):
        def __reversed__(self) -> Generator[str, None, None]:
            """Implement :func:`reversed(self)<reversed>`.

            Note
            ----
            This feature requires h5py >= 3.5.

            """
            for k, _ in self._iter_dfs(self._mapping, reverse=True):
                yield k


class RecursiveValuesView(_Mixin[H5PyDataset], _RecursiveMappingView, ValuesView[H5PyDataset]):
    """Create a recursive view of all :class:`<Datasets>h5py.Dataset`.

    Examples
    --------
    .. testsetup:: python

        >>> import os
        >>> filename = os.path.join('tests', 'test_files', '_test.hdf5')
        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    .. doctest:: python
        :skipif: HDF5_EX is not None

        >>> import h5py
        >>> from nanoutils import RecursiveValuesView

        >>> filename: str = ...  # doctest: +SKIP

        >>> with h5py.File(filename, 'a') as f:
        ...     a = f.create_group('a')
        ...     b = f['a'].create_group('b')
        ...
        ...     dset1 = f.create_dataset('dset1', (10,), dtype=float)
        ...     dset2 = f['a'].create_dataset('dset2', (10,), dtype=float)
        ...     dset3 = f['a']['b'].create_dataset('dset3', (10,), dtype=float)
        ...
        ...     print(RecursiveValuesView(f))
        <RecursiveValuesView [<HDF5 dataset "dset3": shape (10,), type "<f8">,
                              <HDF5 dataset "dset2": shape (10,), type "<f8">,
                              <HDF5 dataset "dset1": shape (10,), type "<f8">]>

    .. testcleanup:: python

        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    Parameters
    ----------
    f : :class:`h5py.Group`
        The to-be iterated h5py group of file.

    Returns
    -------
    :class:`ValuesView[h5py.Dataset]<collections.abc.ValuesView>`
        A recursive view of all datasets within the passed group or file.

    """

    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        """Implement :meth:`self == other<object.__eq__>`."""
        cls = type(self)
        if not isinstance(other, cls):
            return NotImplemented
        return Counter(self) == Counter(other)

    def __iter__(self) -> Generator[h5py.Dataset, None, None]:
        """Implement :func:`iter(self)<iter>`."""
        for _, v in self._iter_dfs(self._mapping):
            yield v

    if TYPE_CHECKING or H5PY_VERSION >= Version("3.5.0"):
        def __reversed__(self) -> Generator[h5py.Dataset, None, None]:
            """Implement :func:`reversed(self)<reversed>`.

            Note
            ----
            This feature requires h5py >= 3.5.

            """
            for _, v in self._iter_dfs(self._mapping, reverse=True):
                yield v


class RecursiveItemsView(  # type: ignore[misc]
    _Mixin[Tuple[str, H5PyDataset]],
    _RecursiveMappingView,
    ItemsView[str, H5PyDataset],
):
    """Create a recursive view of all :attr:`~h5py.Dataset.name`/:attr:`~h5py.Dataset` pairs.

    Examples
    --------
    .. testsetup:: python

        >>> import os
        >>> filename = os.path.join('tests', 'test_files', '_test.hdf5')
        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    .. doctest:: python
        :skipif: HDF5_EX is not None

        >>> import h5py
        >>> from nanoutils import RecursiveItemsView

        >>> filename: str = ...  # doctest: +SKIP

        >>> with h5py.File(filename, 'a') as f:
        ...     a = f.create_group('a')
        ...     b = f['a'].create_group('b')
        ...
        ...     dset1 = f.create_dataset('dset1', (10,), dtype=float)
        ...     dset2 = f['a'].create_dataset('dset2', (10,), dtype=float)
        ...     dset3 = f['a']['b'].create_dataset('dset3', (10,), dtype=float)
        ...
        ...     print(RecursiveItemsView(f))
        <RecursiveItemsView [('/a/b/dset3', <HDF5 dataset "dset3": shape (10,), type "<f8">),
                             ('/a/dset2', <HDF5 dataset "dset2": shape (10,), type "<f8">),
                             ('/dset1', <HDF5 dataset "dset1": shape (10,), type "<f8">)]>

    .. testcleanup:: python

        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    Parameters
    ----------
    f : :class:`h5py.Group`
        The to-be iterated h5py group of file.

    Returns
    -------
    :class:`ItemsView[str, h5py.Dataset]<collections.abc.ItemsView>`
        A recursive view of all name/dataset pairs within the passed group or file.

    """

    __slots__ = ()

    def __iter__(self) -> Generator[tuple[str, h5py.Dataset], None, None]:
        """Implement :func:`iter(self)<iter>`."""
        yield from self._iter_dfs(self._mapping)

    if TYPE_CHECKING or H5PY_VERSION >= Version("3.5.0"):
        def __reversed__(self) -> Generator[tuple[str, h5py.Dataset], None, None]:
            """Implement :func:`reversed(self)<reversed>`.

            Note
            ----
            This feature requires h5py >= 3.5.

            """
            yield from self._iter_dfs(self._mapping, reverse=True)


recursive_keys = RecursiveKeysView
recursive_items = RecursiveItemsView
recursive_values = RecursiveValuesView

__doc__ = construct_api_doc(globals())
