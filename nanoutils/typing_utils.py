""":mod:`typing<python:typing>` related types.

Contains aliases for ``python >= 3.8`` exclusive objects related to typing.

Index
-----
=================================== ======================================================================================================================================
:data:`~typing.Literal`             Special typing form to define literal types (a.k.a. value types).
:data:`~typing.Final`               Special typing construct to indicate final names to type checkers.
:func:`~typing.final`               A decorator to indicate final methods and final classes.
:class:`~typing.Protocol`           Base class for protocol classes.
:class:`~typing.SupportsIndex`      An ABC with one abstract method :meth:`~SupportsIndex.__index__`.
:class:`~typing.TypedDict`          A simple typed name space. At runtime it is equivalent to a plain :class:`dict`.
:func:`~typing.runtime_checkable`   Mark a protocol class as a runtime protocol, so that it an be used with :func:`isinstance()` and :func:`issubclass()`.
:data:`~nanoutils.PathType`         An annotation for `path-like <https://docs.python.org/3/glossary.html#term-path-like-object>`_ objects.
=================================== ======================================================================================================================================

API
---
.. currentmodule:: nanoutils
.. data:: PathType
    :value: typing.Union[str, bytes, os.PathLike]

    An annotation for `path-like <https://docs.python.org/3/glossary.html#term-path-like-object>`_ objects.

.. data:: OpenTextMode
    :value: typing.Literal['r', 'r+', '+r', 'rt', 'tr', 'rt+', ...]

    A Literal with accepted values for opening path-like objects in :class:`str` mode.
    See https://github.com/python/typeshed/blob/master/stdlib/3/io.pyi.

.. data:: OpenBinaryMode
    :value: typing.Literal['rb+', 'r+b', '+rb', 'br+', 'b+r', '+br', ...]

    A Literal with accepted values for opening path-like objects in :class:`bytes` mode.
    See https://github.com/python/typeshed/blob/master/stdlib/3/io.pyi.

"""  # noqa: E501

import os
import sys
from abc import abstractmethod
from typing import Union, Iterable

if sys.version_info < (3, 8):
    from typing_extensions import Literal, Final, final, Protocol, TypedDict, runtime_checkable

    @runtime_checkable
    class SupportsIndex(Protocol):
        """An ABC with one abstract method :meth:`__index__`."""

        __slots__: Union[str, Iterable[str]] = ()

        @abstractmethod
        def __index__(self) -> int:
            """Return **self** converted to an :class:`int`, if **self** is suitable for use as an index into a :class:`list`."""  # noqa: E501
            pass

else:
    from typing import Literal, Final, final, Protocol, TypedDict, SupportsIndex, runtime_checkable

__all__ = [
    'Literal', 'Final', 'final', 'Protocol', 'SupportsIndex', 'TypedDict', 'runtime_checkable',
    'PathType', 'OpenTextMode', 'OpenBinaryMode'
]

PathType = Union[str, bytes, os.PathLike]

OpenTextMode = Literal[
    'r', 'r+', '+r', 'rt', 'tr', 'rt+', 'r+t', '+rt', 'tr+', 't+r', '+tr',
    'w', 'w+', '+w', 'wt', 'tw', 'wt+', 'w+t', '+wt', 'tw+', 't+w', '+tw',
    'a', 'a+', '+a', 'at', 'ta', 'at+', 'a+t', '+at', 'ta+', 't+a', '+ta',
    'x', 'x+', '+x', 'xt', 'tx', 'xt+', 'x+t', '+xt', 'tx+', 't+x', '+tx',
    'U', 'rU', 'Ur', 'rtU', 'rUt', 'Urt', 'trU', 'tUr', 'Utr',
]

OpenBinaryMode = Literal[
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
