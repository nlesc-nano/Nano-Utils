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
import io
from collections import Counter
from collections.abc import Generator, MappingView, Iterator
from typing import NoReturn

if sys.version_info >= (3, 9):
    from collections.abc import KeysView, ValuesView, ItemsView
else:
    from typing import KeysView, ValuesView, ItemsView

from .utils import raise_if, construct_api_doc, VersionInfo

try:
    import h5py
    from h5py import Dataset as H5PyDataset
    H5PY_EX: None | Exception = None
    H5PY_VERSION = VersionInfo._make(h5py.version.version_tuple[:3])
except Exception as ex:
    H5PY_EX = ex
    H5PY_VERSION = VersionInfo(0, 0, 0)
    H5PyDataset = "h5py.Dataset"

__all__ = [
    'recursive_keys',
    'recursive_values',
    'recursive_items',
    'RecursiveKeysView',
    'RecursiveValuesView',
    'RecursiveItemsView',
]


class _RecursiveMappingView(MappingView, metaclass=abc.ABCMeta):
    """Base class for recursive group or file views."""

    __slots__ = ("__weakref__",)

    _mapping: h5py.Group
    __hash__ = None  # type: ignore[assignment]

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
        iterator = iter(self)

        stream = io.StringIO()
        stream.write(f"<{cls.__name__} [")

        # Print size-1 view on a single line by special casing the first element
        try:
            item = next(iterator)
        except StopIteration:
            pass
        else:
            stream.write(repr(item))
        for item in iterator:
            stream.write(f",\n{indent}{item!r}")

        stream.write("]>")
        return stream.getvalue()

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

    if H5PY_VERSION >= (3, 5, 0):
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


class RecursiveKeysView(_RecursiveMappingView, KeysView[str]):
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

    if H5PY_VERSION >= (3, 5, 0):
        def __reversed__(self) -> Generator[str, None, None]:
            """Implement :func:`reversed(self)<reversed>`.

            Note
            ----
            This feature requires h5py >= 3.5.

            """
            for k, _ in self._iter_dfs(self._mapping, reverse=True):
                yield k


class RecursiveValuesView(_RecursiveMappingView, ValuesView[H5PyDataset]):
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

    if H5PY_VERSION >= (3, 5, 0):
        def __reversed__(self) -> Generator[h5py.Dataset, None, None]:
            """Implement :func:`reversed(self)<reversed>`.

            Note
            ----
            This feature requires h5py >= 3.5.

            """
            for _, v in self._iter_dfs(self._mapping, reverse=True):
                yield v


class RecursiveItemsView(_RecursiveMappingView, ItemsView[str, H5PyDataset]):
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

    if H5PY_VERSION >= (3, 5, 0):
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
