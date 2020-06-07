""":mod:`typing<python:typing>` related types.

Contains aliases for ``python >= 3.8`` exclusive objects related to typing.

See Also
--------
.. image:: https://badge.fury.io/py/typing-extensions.svg
    :target: https://badge.fury.io/py/typing-extensions

The typing module: Support for gradual typing as defined by `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_.

At large scale, the structure of the module is following:

* Imports and exports, all public names should be explicitly added to :data:`__all__`.
* Internal helper functions: these should never be used in code outside this module.
* :class:`~typing._SpecialForm` and its instances (special forms): :data:`~typing.Any`,
  :data:`~typing.NoReturn`, :data:`~typing.ClassVar`, :data:`~typing.Union` and :data:`~typing.Optional`.
* Two classes whose instances can be type arguments in addition to types:
  :class:`~typing.ForwardRef` and :class:`~typing.TypeVar`.
* The core of internal generics API: _GenericAlias and _VariadicGenericAlias, the latter is
  currently only used by :data:`~typing.Tuple` and :data:`~typing.Callable`.
  All subscripted types like :code:`X[int]`, :code:`Union[int, str]`,
  *etc.*, are instances of either of these classes.
* The public counterpart of the generics API consists of two classes: :class:`~typing.Generic`
  and :class:`~typing.Protocol`.
* Public helper functions: :func:`~typing.get_type_hints`, :func:`~typing.overload`,
  :func:`~typing.cast`, :func:`~typing.no_type_check`, :func:`~typing.no_type_check_decorator`.
* Generic aliases for :mod:`collections.abc` ABCs and few additional protocols.
* Special types: :func:`~typing.NewType`, :class:`~typing.NamedTuple` and :class:`~typing.TypedDict`.
* Wrapper submodules for :mod:`re` and :mod:`io` related types.


Index
-----
=================================== ======================================================================================================================================
:data:`~typing.Literal`             Special typing form to define literal types (a.k.a. value types).
:data:`~typing.Final`               Special typing construct to indicate final names to type checkers.
:func:`~typing.final`               A decorator to indicate final methods and final classes.
:class:`~typing.Protocol`           Base class for protocol classes.
:class:`~typing.SupportsIndex`      An ABC with one abstract method :class:`~object.__index__()`.
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
    'PathType'
]

# See https://github.com/python/typeshed/blob/master/stdlib/3/os/path.pyi.
PathType = Union[str, bytes, os.PathLike]
