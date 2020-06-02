"""A module with empty (immutable) iterables.

can be used as default arguments for functions.

Index
-----
=========================== =================================================
:data:`EMPTY_SEQUENCE`      An empty :class:`~collections.abc.Sequence`.
:data:`EMPTY_MAPPING`       An empty :class:`~collections.abc.Mapping`.
:data:`EMPTY_COLLECTION`    An empty :class:`~collections.abc.Collection`.
:data:`EMPTY_SET`           An empty :class:`~collections.abc.Set`.
=========================== =================================================

API
---
.. currentmodule:: nanoutils
.. data:: EMPTY_SEQUENCE
    :value: ()

    An empty :class:`~collections.abc.Sequence`.

.. data:: EMPTY_MAPPING
    :value: mappingproxy({})

    An empty :class:`~collections.abc.Mapping`.

.. data:: EMPTY_COLLECTION
    :value: frozenset()

    An empty :class:`~collections.abc.Collection`.

.. data:: EMPTY_SET
    :value: frozenset()

    An empty :class:`~collections.abc.Set`.

"""  # noqa: E501

from types import MappingProxyType
from typing import Mapping, Collection, Sequence, AbstractSet

__all__ = ['EMPTY_SEQUENCE', 'EMPTY_MAPPING', 'EMPTY_COLLECTION', 'EMPTY_SET']

#: An empty :class:`~collections.abc.Sequence`.
EMPTY_SEQUENCE: Sequence = ()

#: An empty :class:`~collections.abc.Mapping`.
EMPTY_MAPPING: Mapping = MappingProxyType({})

#: An empty :class:`~collections.abc.Collection`.
EMPTY_COLLECTION: Collection = frozenset()

#: An empty :class:`~collections.abc.Set`.
EMPTY_SET: AbstractSet = frozenset()
