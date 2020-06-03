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
=================================== ======================================================================================================================================

"""  # noqa: E501

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
    'Literal', 'Final', 'final', 'Protocol', 'SupportsIndex', 'TypedDict', 'runtime_checkable'
]
