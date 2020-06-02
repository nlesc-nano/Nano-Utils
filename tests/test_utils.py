"""Tests for :mod:`nanoutils.utils`."""

from assertionlib import assertion
from nanoutils import set_docstring


def test_set_docstring() -> None:
    """Tests for :func:`nanoutils.set_docstring`."""

    @set_docstring('TEST')
    def func1():
        pass

    @set_docstring(None)
    def func2():
        pass

    assertion.eq(func1.__doc__, 'TEST')
    assertion.eq(func2.__doc__, None)
