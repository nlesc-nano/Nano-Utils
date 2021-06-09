"""Types related to the builtin :mod:`typing<python:typing>` module.

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
========================================== ======================================================================================================================================
:data:`~typing.Literal`                    Special typing form to define literal types (a.k.a. value types).
:data:`~typing.Final`                      Special typing construct to indicate final names to type checkers.
:func:`~typing.final`                      A decorator to indicate final methods and final classes.
:class:`~typing.Protocol`                  Base class for protocol classes.
:class:`~typing.SupportsIndex`             An ABC with one abstract method :meth:`~object.__index__()`.
:class:`~typing.TypedDict`                 A simple typed name space. At runtime it is equivalent to a plain :class:`dict`.
:func:`~typing.runtime_checkable`          Mark a protocol class as a runtime protocol, so that it an be used with :func:`isinstance()` and :func:`issubclass()`.
:data:`~nanoutils.PathType`                An annotation for `path-like <https://docs.python.org/3/glossary.html#term-path-like-object>`_ objects.
:data:`~numpy.typing.ArrayLike`            Objects that can be converted to arrays (see :class:`numpy.ndarray`).
:data:`~numpy.typing.DTypeLike`            Objects that can be converted to dtypes (see :class:`numpy.dtype`).
:data:`ShapeLike<numpy.typing._ShapeLike>` Objects that can serve as valid array shapes.
========================================== ======================================================================================================================================

API
---
.. currentmodule:: nanoutils
.. data:: PathType
    :value: typing.Union[str, bytes, os.PathLike]

    An annotation for `path-like <https://docs.python.org/3/glossary.html#term-path-like-object>`_ objects.

"""  # noqa: E501

import os
import sys
from typing import Union, TYPE_CHECKING

if sys.version_info < (3, 8):
    from typing_extensions import Literal, Final, final, Protocol, TypedDict, runtime_checkable, SupportsIndex  # noqa: E501
else:
    from typing import Literal, Final, final, Protocol, TypedDict, SupportsIndex, runtime_checkable

if TYPE_CHECKING:
    # Requires numpy >= 1.20
    from numpy.typing import ArrayLike, DTypeLike, _ShapeLike as ShapeLike
    from numpy.typing import DTypeLike as DtypeLike

else:
    ArrayLike = 'numpy.typing.ArrayLike'
    DTypeLike = 'numpy.typing.DTypeLike'
    DtypeLike = DTypeLike
    ShapeLike = 'numpy.typing._ShapeLike'

__all__ = [
    'Literal', 'Final', 'final', 'Protocol', 'SupportsIndex', 'TypedDict', 'runtime_checkable',

    'PathType',

    'ArrayLike', 'DTypeLike', 'DtypeLike', 'ShapeLike'
]

# See https://github.com/python/typeshed/blob/master/stdlib/3/os/path.pyi.
PathType = Union[str, bytes, os.PathLike]
