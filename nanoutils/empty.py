"""A module with empty (immutable) iterables.

Can be used as default arguments for functions.

Index
-----
===================================== =================================================
:data:`~nanoutils.EMPTY_CONTAINER`     An empty :class:`~collections.abc.Container`.
:data:`~nanoutils.EMPTY_COLLECTION`    An empty :class:`~collections.abc.Collection`.
:data:`~nanoutils.EMPTY_SET`           An empty :class:`~collections.abc.Set`.
:data:`~nanoutils.EMPTY_SEQUENCE`      An empty :class:`~collections.abc.Sequence`.
:data:`~nanoutils.EMPTY_MAPPING`       An empty :class:`~collections.abc.Mapping`.
===================================== =================================================

API
---
.. currentmodule:: nanoutils
.. data:: EMPTY_CONTAINER
    :type: Container
    :value: frozenset()

    An empty :class:`~collections.abc.Container`.

.. data:: EMPTY_COLLECTION
    :type: Collection
    :value: frozenset()

    An empty :class:`~collections.abc.Collection`.

.. data:: EMPTY_SET
    :type: Set
    :value: frozenset()

    An empty :class:`~collections.abc.Set`.

.. data:: EMPTY_SEQUENCE
    :type: Sequence
    :value: ()

    An empty :class:`~collections.abc.Sequence`.

.. data:: EMPTY_MAPPING
    :type: Mapping
    :value: mappingproxy({})

    An empty :class:`~collections.abc.Mapping`.

"""

from types import MappingProxyType
from typing import Mapping, Collection, Sequence, AbstractSet, Container

__all__ = [
    'EMPTY_SEQUENCE', 'EMPTY_MAPPING', 'EMPTY_COLLECTION', 'EMPTY_SET', 'EMPTY_CONTAINER'
]

#: An empty :class:`~collections.abc.Sequence`.
EMPTY_SEQUENCE: Sequence = ()

#: An empty :class:`~collections.abc.Mapping`.
EMPTY_MAPPING: Mapping = MappingProxyType({})

#: An empty :class:`~collections.abc.Collection`.
EMPTY_COLLECTION: Collection = frozenset()

#: An empty :class:`~collections.abc.Set`.
EMPTY_SET: AbstractSet = frozenset()

#: An empty :class:`~collections.abc.Container`.
EMPTY_CONTAINER: Container = frozenset()
