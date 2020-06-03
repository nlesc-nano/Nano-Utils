"""Tests for :mod:`nanoutils.typing_utils`."""

import sys

from assertionlib import assertion
from nanoutils import Literal, Final, final, Protocol, TypedDict, SupportsIndex, runtime_checkable

if sys.version_info < (3, 8):
    import typing_extensions as t
else:
    import typing as t


def test_typing() -> None:
    """Tests for :mod:`nanoutils.typing_utils`."""
    assertion.is_(Literal, t.Literal)
    assertion.is_(Final, t.Final)
    assertion.is_(final, t.final)
    assertion.is_(Protocol, t.Protocol)
    assertion.is_(TypedDict, t.TypedDict)
    assertion.is_(runtime_checkable, t.runtime_checkable)

    if sys.version_info >= (3, 8):
        assertion.is_(SupportsIndex, t.SupportsIndex)
    else:
        assertion.contains(SupportsIndex.__bases__, Protocol)
        assertion.hasattr(SupportsIndex, '__index__')
