"""Tests for :mod:`nanoutils.empty`."""

from collections import abc

from nanoutils import EMPTY_SEQUENCE, EMPTY_MAPPING, EMPTY_COLLECTION, EMPTY_SET, EMPTY_CONTAINER
from assertionlib import assertion


def test_empty() -> None:
    """Tests for :mod:`nanoutils.empty`."""
    assertion.isinstance(EMPTY_SEQUENCE, abc.Sequence)
    assertion.isinstance(EMPTY_MAPPING, abc.Mapping)
    assertion.isinstance(EMPTY_COLLECTION, abc.Collection)
    assertion.isinstance(EMPTY_SET, abc.Set)
    assertion.isinstance(EMPTY_CONTAINER, abc.Container)
    assertion.not_(EMPTY_SEQUENCE)  # type: ignore
    assertion.not_(EMPTY_MAPPING)  # type: ignore
    assertion.not_(EMPTY_COLLECTION)  # type: ignore
    assertion.not_(EMPTY_SET)  # type: ignore
    assertion.not_(EMPTY_CONTAINER)  # type: ignore
