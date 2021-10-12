from __future__ import annotations

import weakref
import copy
import pickle
import sys
import textwrap
import string
from typing import TYPE_CHECKING, no_type_check
from collections.abc import KeysView, ValuesView, ItemsView, Iterator, Callable

import pytest
from assertionlib import assertion
from nanoutils import UserMapping, MutableUserMapping
from nanoutils._user_dict import _DictLike

if TYPE_CHECKING:
    import _pytest

try:
    from IPython.lib.pretty import pretty
except ModuleNotFoundError:
    IPYTHON: bool = False
    pretty = NotImplemented
else:
    IPYTHON = True


class BasicMapping:
    def __init__(self, dct: dict[str, int]) -> None:
        self._dict = dct

    def keys(self) -> Iterator[str]:
        return iter(self._dict.keys())

    def __getitem__(self, key: str) -> int:
        return self._dict[key]


@pytest.mark.parametrize("obj", [
    UserMapping(a=0, b=1, c=2),
    MutableUserMapping(a=0, b=1, c=2),
], ids=["UserMapping", "MutableUserMapping"])
class TestUserMapping:
    @pytest.mark.parametrize("inp", [
        {"a": 0, "b": 1, "c": 2},
        BasicMapping({"a": 0, "b": 1, "c": 2}),
        [("a", 0), ("b", 1), ("c", 2)],
    ], ids=["dict", "BasicMapping", "Iterable"])
    def test_init(self, obj: UserMapping[str, int], inp: _DictLike[str, int]) -> None:
        cls = type(obj)
        assertion.eq(cls(inp), obj)
        if not isinstance(inp, list):
            assertion.eq(cls(**inp), obj)  # type: ignore[arg-type]

    def test_pickle(self, obj: UserMapping[str, int]) -> None:
        out = pickle.loads(pickle.dumps(obj))
        assertion.eq(out, obj)

    def test_weakref(self, obj: UserMapping[str, int]) -> None:
        out = weakref.ref(obj)()
        assertion.eq(out, obj)

    def test_copy(self, obj: UserMapping[str, int]) -> None:
        out = copy.copy(obj)
        assertion.eq(out, obj)

    def test_deepcopy(self, obj: UserMapping[str, int]) -> None:
        out = copy.deepcopy(obj)
        assertion.eq(out, obj)
        assertion.is_not(out._dict, obj._dict)

    def test_copy_meth(self, obj: UserMapping[str, int]) -> None:
        out = obj.copy()
        assertion.eq(out, obj)
        assertion.is_not(out._dict, obj._dict)

    def test_eq(self, obj: UserMapping[str, int]) -> None:
        assertion.eq(obj, obj)
        assertion.ne(obj, 1)

    @pytest.mark.parametrize("key,value", [("a", 0), ("b", 1), ("c", 2)])
    def test_getitem(self, obj: UserMapping[str, int], key: str, value: int) -> None:
        assertion.eq(obj[key], value)

    @pytest.mark.parametrize("str_func", [
        str,
        repr,
        pytest.param(pretty, marks=pytest.mark.skipif(not IPYTHON, reason="Requires IPython")),
    ], ids=["str", "repr", "pretty"])
    def test_repr(self, obj: UserMapping[str, int], str_func: Callable[[object], str]) -> None:
        string1 = f"{type(obj).__name__}({{'a': 0, 'b': 1, 'c': 2}})"
        assertion.str_eq(obj, string1, str_converter=str_func)

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
        assertion.str_eq(ref2, string2, str_converter=str_func)

    @pytest.mark.skipif(not IPYTHON, reason="Rquires IPython")
    def test_pretty_repr(self, obj: UserMapping[str, int]) -> None:
        string1 = f"{type(obj).__name__}({{'a': 0, 'b': 1, 'c': 2}})"
        assertion.str_eq(obj, string1, str_converter=pretty)

    def test_hash(self, obj: UserMapping[str, int]) -> None:
        if isinstance(obj, MutableUserMapping):
            with pytest.raises(TypeError):
                hash(obj)
        else:
            assertion.isinstance(hash(obj), int)

    def test_iter(self, obj: UserMapping[str, int]) -> None:
        assertion.eq(list(iter(obj)), ["a", "b", "c"])

    def test_len(self, obj: UserMapping[str, int]) -> None:
        assertion.len_eq(obj, 3)

    def test_contains(self, obj: UserMapping[str, int]) -> None:
        assertion.contains(obj, "a")
        assertion.contains(obj, "d", invert=True)

    def test_keys(self, obj: UserMapping[str, int]) -> None:
        assertion.isinstance(obj.keys(), KeysView)
        assertion.eq(list(obj.keys()), ["a", "b", "c"])

    def test_values(self, obj: UserMapping[str, int]) -> None:
        assertion.isinstance(obj.values(), ValuesView)
        assertion.eq(list(obj.values()), [0, 1, 2])

    def test_items(self, obj: UserMapping[str, int]) -> None:
        assertion.isinstance(obj.items(), ItemsView)
        assertion.eq(list(obj.items()), [("a", 0), ("b", 1), ("c", 2)])

    def test_fromkeys(self, obj: UserMapping[str, int]) -> None:
        cls = type(obj)
        dct = cls.fromkeys(obj)
        assertion.isinstance(dct, cls)
        assertion.eq(dct.keys(), obj.keys())

    def test_key_completions(self, obj: UserMapping[str, int]) -> None:
        assertion.isinstance(obj._ipython_key_completions_(), KeysView)
        assertion.eq(obj._ipython_key_completions_(), obj.keys())

    def test_get(self, obj: UserMapping[str, int]) -> None:
        assertion.eq(obj.get("a"), 0)
        assertion.is_(obj.get("d"), None)
        assertion.eq(obj.get("d", 6), 6)

    @pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires python >= 3.8")
    @no_type_check
    def test_reversed(self, obj: UserMapping[str, int]) -> None:
        assertion.eq(list(reversed(obj)), ["c", "b", "a"])

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_or(self, obj: UserMapping[str, int]) -> None:
        b = {"c": 3, "d": 4, "e": 5}
        ref = {"a": 0, "b": 1, "c": 3, "d": 4, "e": 5}
        assertion.eq(obj | b, ref)
        assertion.eq(obj | UserMapping(b), ref)
        with pytest.raises(TypeError):
            1 | obj

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_ror(self, obj: UserMapping[str, int]) -> None:
        b = {"c": 3, "d": 4, "e": 5}
        ref = {"a": 0, "b": 1, "c": 2, "d": 4, "e": 5}
        assertion.eq(b | obj, ref)
        assertion.eq(UserMapping(b) | obj, ref)
        with pytest.raises(TypeError):
            obj | 1

    @pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires python >= 3.9")
    @no_type_check
    def test_ior(self, obj: UserMapping[str, int]) -> None:
        b = {"c": 3, "d": 4, "e": 5}
        if isinstance(obj, MutableUserMapping):
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
    def obj(self, request: _pytest.fixtures.SubRequest) -> MutableUserMapping[str, int]:
        return MutableUserMapping({"a": 0, "b": 1, "c": 2})

    def test_setitem(self, obj: MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        obj["d"] = 3
        assertion.eq(obj["d"], 3)

    def test_delitem(self, obj: MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        del obj["a"]
        assertion.eq(obj, {"b": 1, "c": 2})

    def test_clear(self, obj: MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        obj.clear()
        assertion.eq(obj, {})

    def test_popitem(self, obj: MutableUserMapping[str, int]) -> None:
        obj = obj.copy()
        assertion.eq(obj.popitem(), ("c", 2))

    def test_pop(self, obj: MutableUserMapping[str, int]) -> None:
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
    def test_update(self, obj: MutableUserMapping[str, int], inp: _DictLike[str, int]) -> None:
        obj = obj.copy()
        obj.update(inp, g=6)
        assertion.eq(obj, {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6})
