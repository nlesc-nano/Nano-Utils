"""Tests for :mod:`nanoutils.utils`."""

from inspect import isclass
from functools import partial

from assertionlib import assertion
from nanoutils import set_docstring, get_importable, VersionInfo, version_info


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


def test_get_importable() -> None:
    """Tests for :func:`nanoutils.get_importable`."""
    class Test:
        split = True

    assertion.is_(get_importable('builtins.dict'), dict)
    assertion.is_(get_importable('builtins.dict', validate=isclass), dict)

    assertion.assert_(get_importable, None, exception=TypeError)
    assertion.assert_(get_importable, Test, exception=TypeError)
    assertion.assert_(get_importable, 'builtins.len', validate=isclass, exception=RuntimeError)
    assertion.assert_(get_importable, 'builtins.len', validate=partial(isclass),
                      exception=RuntimeError)


def test_version_info() -> None:
    """Tests for :func:`nanoutils.VersionInfo`."""
    tup1 = VersionInfo(0, 1, 2)
    tup2 = VersionInfo.from_str('0.1.2')
    assertion.eq(tup1, (0, 1, 2))
    assertion.eq(tup2, (0, 1, 2))

    assertion.eq(tup1.micro, tup1.patch)

    assertion.assert_(VersionInfo.from_str, b'0.1.2', exception=TypeError)
    assertion.assert_(VersionInfo.from_str, '0.1.2a', exception=ValueError)
    assertion.assert_(VersionInfo.from_str, '0.1.2.3.4', exception=ValueError)

    assertion.isinstance(version_info, VersionInfo)
