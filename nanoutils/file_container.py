"""An abstract container for reading and writing files.

Index
-----
.. currentmodule:: nanoutils
.. autosummary::
    file_to_context
    AbstractFileContainer

API
---
.. autofunction:: file_to_context
.. autoclass:: AbstractFileContainer
    :members: read, _read, _read_postprocess, write, _write

"""

from __future__ import annotations

import sys
from abc import ABCMeta, abstractmethod
from codecs import decode, encode
from functools import partial
from contextlib import nullcontext
from typing import Dict, Any, AnyStr, Callable, ContextManager, TypeVar, overload, IO, Type

from .typing_utils import PathType, Literal, final
from .utils import _null_func

__all__ = ['AbstractFileContainer', 'file_to_context']

_ST = TypeVar('_ST', bound='AbstractFileContainer')

#: A Literal with accepted values for opening path-like objects in :class:`str` mode.
#: See https://github.com/python/typeshed/blob/master/stdlib/3/io.pyi.
_OpenTextMode = Literal[
    'r', 'r+', '+r', 'rt', 'tr', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr',
    'w', 'w+', '+w', 'wt', 'tw', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw',
    'a', 'a+', '+a', 'at', 'ta', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta',
    'x', 'x+', '+x', 'xt', 'tx', 'xt+', 'x+t', '+xt', 'tx+', 't+x', '+tx',
    'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr',
]

#: A Literal with accepted values for opening path-like objects in :class:`bytes` mode.
#: See https://github.com/python/typeshed/blob/master/stdlib/3/io.pyi.
_OpenBinaryMode = Literal[
    'rb+', 'r+b', '+rb', 'br+', 'b+r', '+br',
    'wb+', 'w+b', '+wb', 'bw+', 'b+w', '+bw',
    'ab+', 'a+b', '+ab', 'ba+', 'b+a', '+ba',
    'xb+', 'x+b', '+xb', 'bx+', 'b+x', '+bx',
    'wb', 'bw',
    'ab', 'ba',
    'xb', 'bx',
    'rb', 'br',
    'rbU', 'rUb', 'Urb', 'brU', 'bUr', 'Ubr',
]


@overload
def file_to_context(
    file: IO[AnyStr],
    **kwargs: Any,
) -> ContextManager[IO[AnyStr]]:
    ...
@overload  # noqa: E302
def file_to_context(  # type: ignore[misc]
    file: int | PathType,
    *,
    mode: _OpenTextMode = ...,
    **kwargs: Any,
) -> ContextManager[IO[str]]:
    ...
@overload  # noqa: E302
def file_to_context(
    file: int | PathType,
    *,
    mode: _OpenBinaryMode = ...,
    **kwargs: Any,
) -> ContextManager[IO[bytes]]:
    ...
def file_to_context(file, **kwargs):  # noqa: E302
    r"""Take a path- or file-like object and return an appropiate context manager.

    Passing a path-like object will supply it to :func:`open`,
    while passing a file-like object will pass it to :func:`contextlib.nullcontext`.

    Examples
    --------
    .. code:: python

        >>> from io import StringIO
        >>> from nanoutils import file_to_context

        >>> path_like = 'file_name.txt'
        >>> file_like = StringIO('this is a file-like object')

        >>> context1 = file_to_context(file_like)
        >>> with context1 as f1:
        ...     ...  # doctest: +SKIP

        >>> context2 = file_to_context(path_like)  # doctest: +SKIP
        >>> with context2 as f2:  # doctest: +SKIP
        ...     ... # insert operations here  # doctest: +SKIP

    Parameters
    ----------
    file : :class:`str`, :class:`bytes`, :class:`os.PathLike` or :class:`~typing.IO`
        A `path- <https://docs.python.org/3/glossary.html#term-path-like-object>`_ or
        `file-like <https://docs.python.org/3/glossary.html#term-file-object>`_ object.
    **kwargs : :data:`~typing.Any`
        Further keyword arguments for :func:`open`.
        Only relevant if **file** is a path-like object.

    Returns
    -------
    :class:`ContextManager[IO]<typing.ContextManager>`
        An initialized context manager.
        Entering the context manager will return a file-like object.

    """
    # path-like object
    try:
        return open(file, **kwargs)

    # a file-like object (hopefully)
    except TypeError:
        return nullcontext(file)


class AbstractFileContainer(metaclass=ABCMeta):
    """An abstract container for reading and writing files.

    Two public methods are defined within this class:

    * :meth:`AbstractFileContainer.read`: Construct a new instance from this object's class by
      reading the content to a file or file object.
      How the content of the to-be read file is parsed has to be defined in the
      :meth:`AbstractFileContainer._read` abstract method.
      Additional post processing, after the new instance has been created, can be performed
      with :meth:`AbstractFileContainer._read_postprocess`
    * :meth:`AbstractFileContainer.write`: Write the content of this instance to an opened
      file or file object.
      How the content of the to-be exported class instance is parsed has to be defined in
      the :meth:`AbstractFileContainer._write`

    Examples
    --------
    .. code:: python

        >>> from io import StringIO
        >>> from nanoutils import AbstractFileContainer

        >>> class SubClass(AbstractFileContainer):
        ...     def __init__(self, value: str):
        ...         self.value = value
        ...
        ...     @classmethod
        ...     def _read(cls, file_obj, decoder):
        ...         value = decoder(file_obj.read())
        ...         return {'value': value}
        ...
        ...     def _write(self, file_obj, encoder):
        ...         value = encoder(self.value)
        ...         file_obj.write(value)

        >>> file1 = StringIO('This is a file-like object')
        >>> file2 = StringIO()

        >>> obj = SubClass.read(file1)
        >>> obj.write(file2)

        >>> print(file2.getvalue())
        This is a file-like object

    """

    __slots__ = ()

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an instance."""
        raise NotImplementedError("Trying to call an abstract method")

    @final
    @classmethod
    def read(
        cls: Type[_ST],
        file: PathType | IO[Any],
        bytes_decoding: None | str = None,
        **kwargs: Any,
    ) -> _ST:
        r"""Construct a new instance from this object's class by reading the content of **file**.

        Parameters
        ----------
        file : :class:`str`, :class:`bytes`, :class:`os.PathLike` or :class:`~typing.IO`
            A `path- <https://docs.python.org/3/glossary.html#term-path-like-object>`_ or
            `file-like <https://docs.python.org/3/glossary.html#term-file-object>`_ object.
        bytes_decoding : :class:`str`, optional
            The type of encoding to use when reading from **file**
            when it will be/is be opened in :class:`bytes` mode.
            This value should be left empty otherwise.
        \**kwargs : :data:`~typing.Any`
            Further keyword arguments for :func:`open`.
            Only relevant if **file** is a path-like object.

        Returns
        -------
        :class:`nanoutils.AbstractFileContainer`
            A new instance constructed from **file**.

        """  # noqa
        kwargs.setdefault('mode', 'r')
        context_manager = file_to_context(file, **kwargs)

        with context_manager as f:
            try:
                assert f.readable()
            except (TypeError, AttributeError) as ex:
                raise TypeError("'file' expected a file- or path-like object; "
                                f"observed type: {file.__class__.__name__!r}") from ex
            except AssertionError:
                f.read()  # This will raise an :exc:`io.UnsupportedOperation`

            if bytes_decoding is None:
                decoder: Callable[[Any], str] = _null_func
            else:
                decoder = partial(decode, encoding=bytes_decoding)  # type: ignore
            cls_dict = cls._read(f, decoder)

        ret = cls(**cls_dict)
        ret._read_postprocess()
        return ret

    @classmethod
    @abstractmethod
    def _read(cls, file_obj: IO[AnyStr], decoder: Callable[[AnyStr], str]) -> Dict[str, Any]:
        r"""A helper function for :meth:`~AbstractFileContainer.read`.

        Parameters
        ----------
        file_obj : :class:`IO[AnyStr]<typing.IO>`
            A file-like object opened in read mode.
        decoder : :data:`Callable[[AnyStr], str]<typing.Callable>`
            A function for converting the items of **file_obj** into strings.

        Returns
        -------
        :class:`Dict[str, Any]<typing.Dict>`
            A dictionary with keyword arguments for a new instance of this objects' class.

        See Also
        --------
        :meth:`AbstractFileContainer.read`
            Construct a new instance from this object's class by reading the content of **file**.

        """
        raise NotImplementedError('Trying to call an abstract method')

    def _read_postprocess(self) -> None:
        r"""Post process new instances created by :meth:`~AbstractFileContainer.read`.

        :rtype: :data:`None`

        See Also
        --------
        :meth:`AbstractFileContainer.read`
            Construct a new instance from this object's class by reading the content of **file**.

        """
        pass

    @final
    def write(
        self,
        file: PathType | IO[Any] = sys.stdout,
        bytes_encoding: None | str = None,
        **kwargs: Any,
    ) -> None:
        r"""Write the content of this instance to **file**.

        Parameters
        ----------
        file : :class:`str`, :class:`bytes`, :class:`os.PathLike` or :class:`~typing.IO`
            A `path- <https://docs.python.org/3/glossary.html#term-path-like-object>`_ or
            `file-like <https://docs.python.org/3/glossary.html#term-file-object>`_ object.
            Defaults to :data:`sys.stdout` if not specified.
        bytes_encoding : :class:`str`, optional
            The type of encoding to use when writing to **file**
            when it will be/is be opened in :class:`bytes` mode.
            This value should be left empty otherwise.
        \**kwargs : :data:`~typing.Any`
            Further keyword arguments for :func:`open`.
            Only relevant if **file** is a path-like object.


        :rtype: :data:`None`

        """
        kwargs.setdefault('mode', 'w')
        context_manager = file_to_context(file, **kwargs)

        with context_manager as f:
            try:
                assert f.writable()
            except (TypeError, AttributeError) as ex:
                raise TypeError("'file' expected a file- or path-like object; "
                                f"observed type: {file.__class__.__name__!r}") from ex
            except AssertionError:
                f.write(None)  # This will raise an :exc:`io.UnsupportedOperation`

            if bytes_encoding is None:
                encoder: Callable[[str], str | bytes] = _null_func
            else:
                encoder = partial(encode, encoding=bytes_encoding)
            self._write(f, encoder)

    @abstractmethod
    def _write(self, file_obj: IO[AnyStr], encoder: Callable[[str], AnyStr]) -> None:
        r"""A helper function for :meth:`~AbstractFileContainer.write`.

        Parameters
        ----------
        file_obj : :class:`IO[AnyStr]<typing.IO>`
            A file-like object opened in write mode.
        encoder : :class:`Callable[[str], AnyStr]<typing.Callable>`
            A function for converting strings into either :class:`str` or :class:`bytes`,
            the exact type matching that of **file_obj**.


        :rtype: :data:`None`

        See Also
        --------
        :meth:`AbstractFileContainer.write`:
            Write the content of this instance to **file**.

        """
        raise NotImplementedError('Trying to call an abstract method')
