"""An abstract container for reading and writing files.

Index
-----
.. currentmodule:: FOX.io.file_container
.. autosummary::
    AbstractFileContainer

API
---
.. autoclass:: AbstractFileContainer
    :members:
    :private-members:
    :special-members:

"""

import sys
import os
import io
from functools import partial
from abc import ABCMeta, abstractmethod
from codecs import iterdecode, encode
from typing import (
    Dict, Optional, Any, Iterable, Iterator, Union, AnyStr, Callable, ContextManager,
    TypeVar, AnyStr, overload, IO, Type
)

from .typing_utils import PathType, OpenTextMode, OpenBinaryMode, final

if sys.version_info < (3, 7):
    from contextlib2 import nullcontext
else:
    from contextlib import nullcontext

__all__ = ['AbstractFileContainer']

T = TypeVar('T')
ST = TypeVar('ST', bound='AbstractFileContainer')
CT = TypeVar('CT', bound=Callable)

a = file_to_context('bob')
b = file_to_context('bob', mode='r')
c = file_to_context('bob', mode='rb')


@overload
def file_to_context(file: IO[AnyStr], **kwargs: Any) -> ContextManager[IO[AnyStr]]: ...
@overload
def file_to_context(file: Union[int, PathType], mode: OpenTextMode = ..., **kwargs: Any) -> ContextManager[IO[str]]: ...  # type: ignore
@overload
def file_to_context(file: Union[int, PathType], mode: OpenBinaryMode = ..., **kwargs: Any) -> ContextManager[IO[bytes]]: ...
def file_to_context(file, mode='r', **kwargs):
    r"""Take a path- or file-like object and return an appropiate context manager instance.

    Passing a path-like object will supply it to :func:`open`,
    while passing a file-like object will pass it to :class:`contextlib.nullcontext`.

    Examples
    --------
    .. code:: python

        >>> from io import StringIO
        >>> from nanoutils import file_to_context

        >>> path_like = 'file_name.txt'
        >>> file_like = StringIO('this is a file-like object')

        >>> context1 = file_to_context(path_like)
        >>> context2 = file_to_context(file_like)

        >>> with context1 as f1, with context2 as f2:
        ...     ... # insert operations here

    Parameters
    ----------
    file : :class:`str`, :class:`bytes`, :class:`os.PathLike` or :class:`io.IOBase`
        A `path- <https://docs.python.org/3/glossary.html#term-path-like-object>`_ or
        `file-like <https://docs.python.org/3/glossary.html#term-file-object>`_ object.
    /**kwargs : :data:`~typing.Any`
        Further keyword arguments for :func:`open`.
        Only relevant if **file** is a path-like object.

    Returns
    -------
    :func:`open` or :class:`~contextlib.nullcontext`
        An initialized context manager.
        Entering the context manager will return a file-like object.

    """
    # path-like object
    try:
        return open(file, **kwargs)

    # a file-like object (hopefully)
    except TypeError:
        return nullcontext(file)


def _null_func(obj: T) -> T:
    """Return the passed object."""
    return obj


class AbstractFileContainer(metaclass=ABCMeta):
    """An abstract container for reading and writing files.

    Two public methods are defined within this class:

    * :meth:`AbstractFileContainer.read`: Construct a new instance from this object's class by
        reading the content to a file or file object.
        How the content of the to-be read file is parsed has to be defined in the
        :meth:`AbstractFileContainer._read_iterate` abstract method.
    * :meth:`AbstractFileContainer.write`: Write the content of this instance to an opened
        file or file object.
        How the content of the to-be exported class instance is parsed has to be defined in
        the :meth:`AbstractFileContainer._write_iterate`

    The opening, closing and en-/decoding of files is handled by two above-mentioned methods;
    the parsing
    * :meth:`AbstractFileContainer._read_iterate`
    * :meth:`AbstractFileContainer._write_iterate`

    """

    __slots__: Union[str, Iterable[str]] = ()

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an instance."""
        raise NotImplementedError("Trying to call an abstract method")

    @final
    @classmethod
    def read(cls: Type[ST], file: Union[PathType, IO],
             decoding: Optional[str] = None, **kwargs: Any) -> ST:
        r"""Construct a new instance from this object's class by reading the content of **file**.

        .. _`file object`: https://docs.python.org/3/glossary.html#term-file-object

        Parameters
        ----------
        file : :class:`str`, :class:`bytes`, :class:`os.PathLike` or :class:`io.IOBase`
            A `path- <https://docs.python.org/3/glossary.html#term-path-like-object>`_ or
            `file-like <https://docs.python.org/3/glossary.html#term-file-object>`_ object.
        decoding : :class:`str`, optional
            The type of encoding to use when reading from **file**
            when it will be/is be opened in :class:`bytes` mode.
            This value should be left empty otherwise.
        \**kwargs : :data:`~typing.Any`
            Further keyword arguments for :func:`open`.
            Only relevant if **file** is a path-like object.

        See Also
        --------
        :meth:`AbstractFileContainer._read`
            A helper function for :meth:`~AbstractFileContainer.read`.

        :meth:`AbstractFileContainer._read_postprocess`
            Post processing the class instance created by :meth:`AbstractFileContainer.read`.

        """  # noqa
        kwargs.setdefault('mode', 'r')
        context_manager = file_to_context(file, **kwargs)

        with context_manager as f:
            iterator: Iterator[str] = iter(f) if decoding is None else iterdecode(f, decoding)
            class_dict = cls._read(iterator)

        ret = cls(**class_dict)
        ret._read_postprocess()
        return ret

    @classmethod
    @abstractmethod
    def _read(cls, iterator: Iterator[str]) -> Dict[str, Any]:
        r"""A helper function for :meth:`~AbstractFileContainer.read`.

        Parameters
        ----------
        iterator : :class:`Iterator<collections.abc.Iterator>` [:class:`str`]
            An iterator that returns :class:`str` instances upon iteration.

        Returns
        -------
        :class:`dict` [:class:`str`, :data:`~typing.Any`]
            A dictionary with keyword arguments for a new instance of this objects' class.

        See Also
        --------
        :meth:`AbstractFileContainer.read`
            Construct a new instance from this object's class by reading the content of **file**.

        """  # noqa
        raise NotImplementedError('Trying to call an abstract method')

    def _read_postprocess(self) -> None:
        r"""Post processing the class instance created by :meth:`.read`.

        See Also
        --------
        :meth:`AbstractFileContainer.read`
            The main method for reading files.

        """
        pass

    @final
    def write(self, file: Union[PathType, IO],
              decoding: Optional[str] = None, **kwargs: Any) -> None:
        r"""Write the content of this instance to **file**.

        Parameters
        ----------
        file : :class:`str`, :class:`bytes`, :class:`os.PathLike` or :class:`io.IOBase`
            A `path- <https://docs.python.org/3/glossary.html#term-path-like-object>`_ or
            `file-like <https://docs.python.org/3/glossary.html#term-file-object>`_ object.
        decoding : :class:`str`, optional
            The type of encoding to use when writing to **file**
            when it will be/is be opened in :class:`bytes` mode.
            This value should be left empty otherwise.
        \**kwargs : :data:`~typing.Any`
            Further keyword arguments for :func:`open`.
            Only relevant if **file** is a path-like object.

        See Also
        --------
        :meth:`AbstractFileContainer._write`
            A helper function for :meth:`~AbstractFileContainer.write`.

        """
        kwargs.setdefault('mode', 'w')
        context_manager = file_to_context(file, **kwargs)

        with context_manager as f:
            encoder = _null_func if decoding is None else partial(encode, encoding=decoding)
            self._write(f, encoder)  # type: ignore

    @abstractmethod
    def _write(self, file_obj: IO[AnyStr], encoder: Callable[[str], AnyStr]) -> None:
        r"""A helper function for :meth:`~AbstractFileContainer.write`.

        Example
        -------
        .. code:: python

            >>> iterator = self.as_dict().items()
            >>> for key, value in iterator:
            ...     value: str = f'{key} = {value}'
            ...     write(value)
            >>> return None

        Parameters
        ----------
        file_obj : :class:`IO[AnyStr]<typing.IO>`
            The opened file.
        encoder : :class:`Callable[[bytes], AnyStr]<typing.Callable>`
            A function for converting strings into either :class:`str` or :class:`bytes`,
            the exact type matching that of **file_obj**.

        See Also
        --------
        :meth:`AbstractFileContainer.write`:
            Write the content of this instance to **file**.

        """
        raise NotImplementedError('Trying to call an abstract method')
