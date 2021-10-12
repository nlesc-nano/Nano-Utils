from __future__ import annotations

import sys
import textwrap
from typing import TYPE_CHECKING, no_type_check
from collections.abc import Iterator, Callable

import pytest
from assertionlib import assertion
from nanoutils._user_dict import _DictLike
from nanoutils import DTypeMapping, MutableDTypeMapping
from nanoutils.numpy_utils import NUMPY_EX

if TYPE_CHECKING or NUMPY_EX is None:
    import numpy as np

if TYPE_CHECKING:
    import numpy.typing as npt
    import _pytest

try:
    from IPython.lib.pretty import pretty
except ModuleNotFoundError:
    IPYTHON: bool = False
    pretty = NotImplemented
else:
    IPYTHON = True


class BasicMapping:
    def __init__(self, dct: dict[str, npt.DTypeLike]) -> None:
        self._dict = dct

    def keys(self) -> Iterator[str]:
        return iter(self._dict.keys())

    def __getitem__(self, key: str) -> npt.DTypeLike:
        return self._dict[key]


class Struct:
    a = "i8"
    b = float
    c = (str, 5)
    _private = None
    __private = None


@pytest.mark.skipif(NUMPY_EX is not None, reason="Requires numpy")
class TestDTypeMapping:
    PARAMS = (DTypeMapping, MutableDTypeMapping)

    @pytest.fixture(scope="class", autouse=True, params=PARAMS)
    def obj(self, request: _pytest.fixtures.SubRequest) -> DTypeMapping:
        cls: type[DTypeMapping] = request.param
        return cls(a="i8", b=float, c=(str, 5))

    def test_dtype(self, obj: DTypeMapping) -> None:
        assertion.isinstance(obj.dtype, np.dtype)
        assertion.eq(obj.dtype, [("a", "i8"), ("b", "f8"), ("c", "U5")])
        assertion.eq(np.dtype(obj), obj.dtype)

    def test_from_type(self, obj: DTypeMapping) -> None:
        out = obj.from_type(Struct)
        assertion.eq(out, obj)
        with pytest.raises(TypeError):
            obj.from_type(1)  # type: ignore[arg-type]

    def test_hash(self, obj: DTypeMapping) -> None:
        if isinstance(obj, MutableDTypeMapping):
            with pytest.raises(TypeError):
                hash(obj)
        else:
            obj_reversed = DTypeMapping(reversed(list(obj.items())))
            assertion.eq(hash(obj), hash(obj.copy()))
            assertion.ne(hash(obj), hash(obj_reversed))

    def test_eq(self, obj: DTypeMapping) -> None:
        obj_reversed = DTypeMapping(reversed(list(obj.items())))
        assertion.eq(obj, obj.copy())
        assertion.ne(obj, obj_reversed)
        assertion.ne(obj, 1)

    @pytest.mark.parametrize("name", "abc")
    def test_getattr(self, obj: DTypeMapping, name: str) -> None:
        value = getattr(obj, name)
        assertion.eq(value, obj[name])

        match = f"{type(obj).__name__!r} object has no attribute 'bob'"
        with pytest.raises(AttributeError, match=match):
            del obj.bob

    @pytest.mark.parametrize("name", "abc")
    def test_setattr(self, obj: DTypeMapping, name: str) -> None:
        dtype = np.dtype("S5")
        if isinstance(obj, MutableDTypeMapping):
            obj = obj.copy()
            setattr(obj, name, dtype)
            assertion.eq(obj[name], dtype)
        else:
            match1 = f"{type(obj).__name__!r} object attribute {name!r} is read-only"
            with pytest.raises(AttributeError, match=match1):
                setattr(obj, name, dtype)

        match2 = f"{type(obj).__name__!r} object has no attribute 'bob'"
        with pytest.raises(AttributeError, match=match2):
            obj.bob = None

    @pytest.mark.parametrize("name", "abc")
    def test_delattr(self, obj: DTypeMapping, name: str) -> None:
        if isinstance(obj, MutableDTypeMapping):
            obj = obj.copy()
            delattr(obj, name)
            assertion.contains(obj, name, invert=True)
        else:
            match1 = f"{type(obj).__name__!r} object attribute {name!r} is read-only"
            with pytest.raises(AttributeError, match=match1):
                delattr(obj, name)

        match2 = f"{type(obj).__name__!r} object has no attribute 'bob'"
        with pytest.raises(AttributeError, match=match2):
            del obj.bob

    def test_reversed(self, obj: DTypeMapping) -> None:
        assertion.eq(list(reversed(obj)), ["c", "b", "a"])

    def test_dir(self, obj: DTypeMapping) -> None:
        assertion.issubset(obj.keys(), dir(obj))

    def test_repr(self, obj: DTypeMapping) -> None:
        string1 = textwrap.dedent(f"""
        {type(obj).__name__}(
            a = numpy.dtype('int64'),
            b = numpy.dtype('float64'),
            c = numpy.dtype('<U5'),
        )""").strip()
        assertion.str_eq(obj, string1, str_converter=repr)

        string2 = f"{type(obj).__name__}()"
        assertion.str_eq(type(obj)(), string2, str_converter=repr)

    @pytest.mark.parametrize("str_func", [
        str,
        pytest.param(pretty, marks=pytest.mark.skipif(not IPYTHON, reason="Requires IPython")),
    ], ids=["str", "pretty"])
    def test_str(self, obj: DTypeMapping, str_func: Callable[[object], str]) -> None:
        string = textwrap.dedent(f"""
        {type(obj).__name__}(
            a = int64,
            b = float64,
            c = <U5,
        )""").strip()
        assertion.str_eq(obj, string, str_converter=str_func)

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_or(self, obj: DTypeMapping) -> None:
        b = {"c": "u8", "d": "u4", "e": "u2"}
        ref = DTypeMapping(a="i8", b="f8", c="u8", d="u4", e="u2")
        assertion.eq(obj | b, ref)
        assertion.eq(obj | DTypeMapping(b), ref)
        with pytest.raises(TypeError):
            1 | obj

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_ror(self, obj: DTypeMapping) -> None:
        b = {"c": "u8", "d": "u4", "e": "u2"}
        ref = DTypeMapping(c="U5", d="u4", e="u2", a="i8", b="f8")
        assertion.eq(b | obj, ref)
        assertion.eq(DTypeMapping(b) | obj, ref)
        with pytest.raises(TypeError):
            obj | 1

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_ior(self, obj: DTypeMapping) -> None:
        b = {"c": "u8", "d": "u4", "e": "u2"}
        ref = DTypeMapping(a="i8", b="f8", c="u8", d="u4", e="u2")
        if isinstance(obj, MutableDTypeMapping):
            obj = obj.copy()
            obj |= b
            assertion.eq(obj, ref)
        else:
            with pytest.raises(TypeError):
                obj |= b
        with pytest.raises(TypeError):
            obj |= 1


@pytest.mark.skipif(NUMPY_EX is not None, reason="Requires numpy")
class TestMutableUserMapping:
    @pytest.fixture(scope="class", autouse=True)
    def obj(self, request: _pytest.fixtures.SubRequest) -> MutableDTypeMapping:
        return MutableDTypeMapping(a="i8", b=float, c=(str, 5))

    def test_setitem(self, obj: MutableDTypeMapping) -> None:
        obj = obj.copy()
        obj["d"] = (bytes, 5)
        assertion.eq(obj["d"], np.dtype("S5"))

    @pytest.mark.parametrize("inp", [
        {"c": "u8", "d": "u4", "e": "u2"},
        BasicMapping({"c": "u8", "d": "u4", "e": "u2"}),
        iter({"c": "u8", "d": "u4", "e": "u2"}.items()),
    ], ids=["dict", "BasicMapping", "Iterator"])
    def test_update(self, obj: MutableDTypeMapping, inp: _DictLike[str, npt.DTypeLike]) -> None:
        ref = DTypeMapping(a="i8", b="f8", c="u8", d="u4", e="u2", f="?")
        obj = obj.copy()
        obj.update(inp, f="?")
        assertion.eq(obj, ref)
