"""Tests for :mod:`nanoutils.utils`."""

import sys
from inspect import isclass
from functools import partial

from assertionlib import assertion
from nanoutils import set_docstring, get_importable, VersionInfo, version_info, split_dict


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
    assertion.eq(tup1.micro, tup1.bug)
    assertion.eq(tup1.micro, tup1.maintenance)

    assertion.assert_(VersionInfo.from_str, b'0.1.2', exception=TypeError)
    assertion.assert_(VersionInfo.from_str, '0.1.2bob', exception=ValueError)

    assertion.isinstance(version_info, VersionInfo)


def test_split_dict() -> None:
    """Test :func:`nanoutils.split_dict`."""
    dct1 = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    dct2 = dct1.copy()
    dct3 = dct1.copy()
    dct4 = dct1.copy()
    dct5 = dct1.copy()
    dct6 = dct1.copy()
    dct7 = dct1.copy()
    dct8 = dct1.copy()

    ref1 = {1: 1, 2: 2}
    ref2 = {3: 3, 4: 4, 5: 5}

    split_dict(dct1, keep_keys=[1, 2])
    split_dict(dct2, keep_keys={1, 2})
    split_dict(dct3, keep_keys=iter({1, 2}))
    split_dict(dct4, keep_keys=[1, 2], preserve_order=True)
    assertion.eq(dct1, ref1)
    assertion.eq(dct2, ref1)
    assertion.eq(dct3, ref1)
    assertion.eq(dct4, ref1)
    if sys.version_info[1] > 6:
        assertion.eq(list(dct4.keys()), [1, 2])

    split_dict(dct5, disgard_keys=[1, 2])
    split_dict(dct6, disgard_keys={1, 2})
    split_dict(dct7, disgard_keys=iter({1, 2}))
    split_dict(dct8, disgard_keys=[1, 2], preserve_order=True)
    assertion.eq(dct5, ref2)
    assertion.eq(dct6, ref2)
    assertion.eq(dct7, ref2)
    assertion.eq(dct8, ref2)
    if sys.version_info[1] > 6:
        assertion.eq(list(dct8.keys()), [3, 4, 5])

    assertion.assert_(split_dict, {}, exception=TypeError)
    assertion.assert_(split_dict, {}, keep_keys=[], disgard_keys=[], exception=TypeError)
