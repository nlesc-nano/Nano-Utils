from __future__ import annotations

import weakref
import copy
import pickle
import sys
import textwrap
import string
from typing import TYPE_CHECKING, no_type_check
from collections.abc import KeysView, ValuesView, ItemsView, Iterator

import pytest
from assertionlib import assertion
from nanoutils._user_dict import _UserMapping, _MutableUserMapping, _DictLike

if TYPE_CHECKING:
    import _pytest


class BasicMapping:
    def __init__(self, dct: dict[str, int]) -> None:
        self._dict = dct

    def keys(self) -> Iterator[str]:
        return iter(self._dict.keys())

    def __getitem__(self, key: str) -> int:
        return self._dict[key]


@pytest.mark.parametrize("obj", [
    _UserMapping(a=0, b=1, c=2),
    _MutableUserMapping(a=0, b=1, c=2),
], ids=["_UserMapping", "_MutableUserMapping"])
class TestUserMapping:
    @pytest.mark.parametrize("inp", [
        {"a": 0, "b": 1, "c": 2},
        BasicMapping({"a": 0, "b": 1, "c": 2}),
        [("a", 0), ("b", 1), ("c", 2)],
    ], ids=["dict", "BasicMapping", "Iterable"])
    def test_init(self, obj: _UserMapping[str, int], inp: _DictLike[str, int]) -> None:
        cls = type(obj)
        assertion.eq(cls(inp), obj)
        if not isinstance(inp, list):
            assertion.eq(cls(**inp), obj)  # type: ignore[arg-type]

    def test_pickle(self, obj: _UserMapping[str, int]) -> None:
        out = pickle.loads(pickle.dumps(obj))
        assertion.eq(out, obj)

    def test_weakref(self, obj: _UserMapping[str, int]) -> None:
        out = weakref.ref(obj)()
        assertion.eq(out, obj)

    def test_copy(self, obj: _UserMapping[str, int]) -> None:
        out = copy.copy(obj)
        assertion.eq(out, obj)

    def test_deepcopy(self, obj: _UserMapping[str, int]) -> None:
        out = copy.deepcopy(obj)
        assertion.eq(out, obj)
        assertion.is_not(out._dict, obj._dict)

    def test_copy_meth(self, obj: _UserMapping[str, int]) -> None:
        out = obj.copy()
        assertion.eq(out, obj)
        assertion.is_not(out._dict, obj._dict)

    def test_eq(self, obj: _UserMapping[str, int]) -> None:
        assertion.eq(obj, obj)
        assertion.ne(obj, 1)

    @pytest.mark.parametrize("key,value", [("a", 0), ("b", 1), ("c", 2)])
    def test_getitem(self, obj: _UserMapping[str, int], key: str, value: int) -> None:
        assertion.eq(obj[key], value)

    def test_repr(self, obj: _UserMapping[str, int]) -> None:
        string1 = f"{type(obj).__name__}({{'a': 0, 'b': 1, 'c': 2}})"
        assertion.str_eq(obj, string1)

        cls = type(obj)
        ref2 = cls(zip(string.ascii_lowercase[:12], range(12)))
        string2 = textwrap.dedent(f"""
        {cls.__name__}({{
            'a': 0,
            'b': 1,
            'c': 2,
            'd': 3,
            'e': 4,
            'f': 5,
            'g': 6,
            'h': 7,
            'i': 8,
            'j': 9,
            'k': 10,
            'l': 11,
        }})
        """).strip()
        assertion.str_eq(ref2, string2)

    def test_hash(self, obj: _UserMapping[str, int]) -> None:
        if isinstance(obj, _MutableUserMapping):
            with pytest.raises(TypeError):
                hash(obj)
        else:
            assertion.isinstance(hash(obj), int)

    def test_iter(self, obj: _UserMapping[str, int]) -> None:
        assertion.eq(list(iter(obj)), ["a", "b", "c"])

    def test_len(self, obj: _UserMapping[str, int]) -> None:
        assertion.len_eq(obj, 3)

    def test_contains(self, obj: _UserMapping[str, int]) -> None:
        assertion.contains(obj, "a")
        assertion.contains(obj, "d", invert=True)

    def test_keys(self, obj: _UserMapping[str, int]) -> None:
        assertion.isinstance(obj.keys(), KeysView)
        assertion.eq(list(obj.keys()), ["a", "b", "c"])

    def test_values(self, obj: _UserMapping[str, int]) -> None:
        assertion.isinstance(obj.values(), ValuesView)
        assertion.eq(list(obj.values()), [0, 1, 2])

    def test_items(self, obj: _UserMapping[str, int]) -> None:
        assertion.isinstance(obj.items(), ItemsView)
        assertion.eq(list(obj.items()), [("a", 0), ("b", 1), ("c", 2)])

    def test_fromkeys(self, obj: _UserMapping[str, int]) -> None:
        cls = type(obj)
        dct = cls.fromkeys(obj)
        assertion.isinstance(dct, cls)
        assertion.eq(dct.keys(), obj.keys())

    def test_get(self, obj: _UserMapping[str, int]) -> None:
        assertion.eq(obj.get("a"), 0)
        assertion.is_(obj.get("d"), None)
        assertion.eq(obj.get("d", 6), 6)

    @pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires python >= 3.8")
    @no_type_check
    def test_reversed(self, obj: _UserMapping[str, int]) -> None:
        assertion.eq(list(reversed(obj)), ["c", "b", "a"])

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_or(self, obj: _UserMapping[str, int]) -> None:
        b = {"c": 3, "d": 4, "e": 5}
        ref = {"a": 0, "b": 1, "c": 3, "d": 4, "e": 5}
        assertion.eq(obj | b, ref)
        assertion.eq(obj | _UserMapping(b), ref)
        with pytest.raises(TypeError):
            1 | obj

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_ror(self, obj: _UserMapping[str, int]) -> None:
        b = {"c": 3, "d": 4, "e": 5}
        ref = {"a": 0, "b": 1, "c": 2, "d": 4, "e": 5}
        assertion.eq(b | obj, ref)
        assertion.eq(_UserMapping(b) | obj, ref)
        with pytest.raises(TypeError):
            obj | 1

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_ior(self, obj: _UserMapping[str, int]) -> None:
        b = {"c": 3, "d": 4, "e": 5}
        if isinstance(obj, _MutableUserMapping):
            obj = obj.copy()
            obj |= b
            assertion.eq(obj, {"a": 0, "b": 1, "c": 3, "d": 4, "e": 5})
        else:
            with pytest.raises(TypeError):
                obj |= b
        with pytest.raises(TypeError):
            obj |= 1


class TestMutableUserMapping:
    @pytest.fixture(scope="class", autouse=True)
    def obj(self, request: _pytest.fixtures.SubRequest) -> _MutableUserMapping[str, int]:
        return _MutableUserMapping({"a": 0, "b": 1, "c": 2})

    def test_setitem(self, obj: _MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        obj["d"] = 3
        assertion.eq(obj["d"], 3)

    def test_delitem(self, obj: _MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        del obj["a"]
        assertion.eq(obj, {"b": 1, "c": 2})

    def test_clear(self, obj: _MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        obj.clear()
        assertion.eq(obj, {})

    def test_popitem(self, obj: _MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        assertion.eq(obj.popitem(), ("c", 2))

    def test_pop(self, obj: _MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        assertion.eq(obj.pop("c"), 2)
        assertion.eq(obj, {"a": 0, "b": 1})
        with pytest.raises(KeyError):
            obj.pop("d")
        assertion.eq(obj.pop("d", 6), 6)

    @pytest.mark.parametrize("inp", [
        {"d": 3, "e": 4, "f": 5},
        BasicMapping({"d": 3, "e": 4, "f": 5}),
        [("d", 3), ("e", 4), ("f", 5)],
    ], ids=["dict", "BasicMapping", "Iterable"])
    def test_update(self, obj: _MutableUserMapping[str, int], inp: _DictLike[str, int]) -> None:
        obj = obj.copy()
        obj.update(inp, g=6)
        assertion.eq(obj, {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6})
