"""Utility functions related to unit-testing.

Index
-----
.. currentmodule:: nanoutils
.. autosummary::
{autosummary}

API
---
{autofunction}

"""

from __future__ import annotations

import os
import shutil
import warnings
from typing import TypeVar, Callable, Any, AnyStr, Tuple, cast
from os.path import isdir, isfile, join
from functools import wraps

from .typing_utils import PathType
from .utils import construct_api_doc

__all__ = ['FileNotFoundWarning', 'delete_finally']

_FT = TypeVar('_FT', bound=Callable[..., Any])


class FileNotFoundWarning(ResourceWarning):
    """A :exc:`ResourceWarning` subclass for when a file or directory is requested but doesn’t exist."""  # noqa: E501


def _delete_finally(path: PathType, warn: bool = True) -> None:
    """Helper function for :func:`delete_finally`."""
    try:
        if isdir(path):
            shutil.rmtree(path)
        elif isfile(path):
            os.remove(path)
        elif warn:
            _warning = FileNotFoundWarning(f'No such file or directory: {path!r}')
            warnings.warn(_warning, stacklevel=3)

    # In case an unexpected exception is encountered
    except Exception as ex:
        _warning2 = RuntimeWarning(str(ex))
        _warning2.__cause__ = ex
        warnings.warn(_warning2, stacklevel=3)


def delete_finally(
    *paths: AnyStr | os.PathLike[AnyStr],
    prefix: None | AnyStr = None,
    warn: bool = True,
) -> Callable[[_FT], _FT]:
    r"""A decorater which deletes the specified files and/or directories after calling the deocrated function.

    Examples
    --------
    .. code:: python

        >>> import os
        >>> from nanoutils import delete_finally

        >>> file1 = 'file1.txt'
        >>> dir1 = 'dir1/'
        >>> os.path.isfile(file1) and os.path.isdir(dir1)  # doctest: +SKIP
        True

        >>> @delete_finally(file1, dir1)
        ... def func():
        ...     pass

        >>> func()  # doctest: +SKIP
        >>> os.path.isfile(file1) or os.path.isdir(dir1)  # doctest: +SKIP
        False

    Parameters
    ----------
    \*paths : :class:`str`, :class:`bytes` or :class:`os.PathLike`
        Path-like objects with the names of to-be deleted files and/or directories.
    prefix : :class:`str`, :class:`bytes` or :class:`os.PathLike`, optional
        The directory where all user specified **paths** are located.
        If :data:`None`, asume the files/directories are either absolute or
        located in the current working directory.
    warn : :class:`bool`
        If :data:`True` issue a :exc:`~nanoutils.FileNotFoundWarning` if
        a to-be deleted file or directory cannot be found.

    """  # noqa: E501
    if prefix is not None:
        _PATH_TUP: Tuple[PathType, ...] = tuple(join(prefix, path) for path in paths)
    else:
        _PATH_TUP = paths

    def decorator(func: _FT) -> _FT:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                for path in _PATH_TUP:
                    _delete_finally(path, warn)

        return cast(_FT, wrapper)
    return decorator


__doc__ = construct_api_doc(globals(), decorators={'delete_finally'})
