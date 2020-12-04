"""An module with various :mod:`h5py`-related utilities.

Index
-----
.. currentmodule:: nanoutils
.. autosummary::
{autosummary}

API
---
{autofunction}

"""

from typing import Generator, Tuple, Optional

from .utils import raise_if, construct_api_doc

try:
    import h5py
    H5PY_EX: Optional[Exception] = None
except Exception as ex:
    H5PY_EX = ex

__all__ = ['recursive_keys', 'recursive_values', 'recursive_items']


@raise_if(H5PY_EX)
def recursive_keys(f: 'h5py.Group') -> Generator[str, None, None]:
    """Recursively iterate through all dataset :attr:`names<h5py.Dataset.name>` in **f**.

    Examples
    --------
    .. testsetup:: python

        >>> import os
        >>> filename = os.path.join('tests', 'test_files', 'test.hdf5')
        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    .. code-block:: python

        >>> import h5py
        >>> from nanoutils import recursive_keys

        >>> filename: str = ...  # doctest: +SKIP

        >>> with h5py.File(filename, 'a') as f:
        ...     a = f.create_group('a')
        ...     b = f['a'].create_group('b')
        ...
        ...     dset1 = f.create_dataset('dset1', (10,), dtype=float)
        ...     dset2 = f['a'].create_dataset('dset2', (10,), dtype=float)
        ...     dset3 = f['a']['b'].create_dataset('dset3', (10,), dtype=float)

        >>> with h5py.File(filename, 'r') as f:
        ...     for key in recursive_keys(f):
        ...         print(repr(key))
        '/a/b/dset3'
        '/a/dset2'
        '/dset1'


    .. testcleanup:: python

        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    Parameters
    ----------
    f : :class:`h5py.Group`
        The to-be iterated h5py group of file.

    Yields
    ------
    :class:`str`
        A dataset name within the passed group or file.

    """
    for k, v in f.items():
        if isinstance(v, h5py.Dataset):
            yield v.name
        else:
            for _v in recursive_keys(v):
                yield _v


@raise_if(H5PY_EX)
def recursive_values(f: 'h5py.Group') -> Generator['h5py.Dataset', None, None]:
    """Recursively iterate through all :attr:`<Datasets>h5py.Dataset` in **f**.

    Examples
    --------
    .. testsetup:: python

        >>> import os
        >>> filename = os.path.join('tests', 'test_files', 'test.hdf5')
        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    .. code-block:: python

        >>> import h5py
        >>> from nanoutils import recursive_values

        >>> filename: str = ...  # doctest: +SKIP

        >>> with h5py.File(filename, 'a') as f:
        ...     a = f.create_group('a')
        ...     b = f['a'].create_group('b')
        ...
        ...     dset1 = f.create_dataset('dset1', (10,), dtype=float)
        ...     dset2 = f['a'].create_dataset('dset2', (10,), dtype=float)
        ...     dset3 = f['a']['b'].create_dataset('dset3', (10,), dtype=float)

        >>> with h5py.File(filename, 'r') as f:
        ...     for value in recursive_values(f):
        ...         print(value)
        <HDF5 dataset "dset3": shape (10,), type "<f8">
        <HDF5 dataset "dset2": shape (10,), type "<f8">
        <HDF5 dataset "dset1": shape (10,), type "<f8">


    .. testcleanup:: python

        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    Parameters
    ----------
    f : :class:`h5py.Group`
        The to-be iterated h5py group of file.

    Yields
    ------
    :class:`h5py.Dataset`
        A dataset within the passed group or file.

    """
    for k in recursive_keys(f):
        yield f[k]


@raise_if(H5PY_EX)
def recursive_items(f: 'h5py.Group') -> Generator[Tuple[str, 'h5py.Dataset'], None, None]:
    """Recursively iterate through all :attr:`~h5py.Dataset.name`/:attr:`~h5py.Dataset` pairs in **f**.

    Examples
    --------
    .. testsetup:: python

        >>> import os
        >>> filename = os.path.join('tests', 'test_files', 'test.hdf5')
        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    .. code-block:: python

        >>> import h5py
        >>> from nanoutils import recursive_items

        >>> filename: str = ...  # doctest: +SKIP

        >>> with h5py.File(filename, 'a') as f:
        ...     a = f.create_group('a')
        ...     b = f['a'].create_group('b')
        ...
        ...     dset1 = f.create_dataset('dset1', (10,), dtype=float)
        ...     dset2 = f['a'].create_dataset('dset2', (10,), dtype=float)
        ...     dset3 = f['a']['b'].create_dataset('dset3', (10,), dtype=float)

        >>> with h5py.File(filename, 'r') as f:
        ...     for items in recursive_items(f):
        ...         print(items)
        ('/a/b/dset3', <HDF5 dataset "dset3": shape (10,), type "<f8">)
        ('/a/dset2', <HDF5 dataset "dset2": shape (10,), type "<f8">)
        ('/dset1', <HDF5 dataset "dset1": shape (10,), type "<f8">)


    .. testcleanup:: python

        >>> if os.path.isfile(filename):
        ...     os.remove(filename)

    Parameters
    ----------
    f : :class:`h5py.Group`
        The to-be iterated h5py group of file.

    Yields
    ------
    :class:`str` & :class:`h5py.Dataset`
        A 2-tuple consisting of a datasets' name and the actual dataset itself.

    """  # noqa: E501
    for k in recursive_keys(f):
        yield k, f[k]


__doc__ = construct_api_doc(globals())
