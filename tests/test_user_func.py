from __future__ import annotations

import copy
import pickle
import weakref
import inspect
from typing import Callable, Any, no_type_check

import pytest
from assertionlib import assertion
from nanoutils import UserFunctionType


@UserFunctionType
def function1(a: int) -> bool:
    return a > 5


@UserFunctionType
def function2(a: int) -> bool:
    return a < 5


class MethodTest:
    @UserFunctionType
    def meth(self, a: int) -> bool:
        return a > 5

    @classmethod
    @UserFunctionType
    def meth_class(cls, a: int) -> bool:
        return a > 5

    @staticmethod
    @UserFunctionType
    def meth_static(a: int) -> bool:
        return a > 5


class TestFromResultType:
    """Tests for :class:`FromResult`."""

    @pytest.mark.parametrize("func", [
        lambda i: pickle.loads(pickle.dumps(i)),
        lambda i: weakref.ref(i)(),
        copy.copy,
        copy.deepcopy,
    ], ids=["pickle", "weakref", "copy", "deepcopy"])
    def test_eq(self, func: Callable[[Any], Any]) -> None:
        obj = func(function1)
        assertion.eq(obj, function1)
        assertion.is_(obj, function1)
        assertion.ne(obj, 1)
        assertion.ne(obj, function2)

    def test_hash(self) -> None:
        assertion.assert_(hash, function1)

    def test_dir(self) -> None:
        ref = set(object.__dir__(function1))
        ref |= set(dir(function1.__call__))
        ref_sorted = sorted(ref)

        assertion.eq(ref_sorted, dir(function1))
        for name in ref_sorted:
            assertion.hasattr(function1, name)

    @pytest.mark.parametrize(
        "name", ["__call__", "__code__", "bob", "__module__", "__annotations__"]
    )
    def test_settatr(self, name: str) -> None:
        with pytest.raises(AttributeError):
            setattr(function1, name, None)

    @pytest.mark.parametrize(
        "name", ["__call__", "__code__", "bob", "__module__", "__annotations__"]
    )
    def test_delattr(self, name: str) -> None:
        with pytest.raises(AttributeError):
            delattr(function1, name)

    @no_type_check
    def test_getattr(self) -> None:
        assertion.truth(function1.__call__)
        assertion.is_(function1.__code__, function1.__call__.__code__)
        with pytest.raises(AttributeError):
            function1.bob

    def test_init(self) -> None:
        with pytest.raises(TypeError):
            UserFunctionType(function1)

    def test_call(self) -> None:
        assertion.truth(function1(10))
        assertion.truth(function1(0), invert=True)

    @pytest.mark.parametrize("func", [repr, str], ids=["repr", "str"])
    def test_repr(self, func: Callable[[Any], str]) -> None:
        ref = "<UserFunctionType instance test_user_func.function1(a: 'int') -> 'bool'>"
        assertion.eq(func(function1), ref)

    def test_signature(self) -> None:
        sgn1 = inspect.signature(function1)
        sgn2 = inspect.signature(function1.__call__)
        assertion.eq(sgn1, sgn2)

    def test_get(self) -> None:
        obj = MethodTest()
        assertion.assert_(obj.meth, 10)
        assertion.assert_(obj.meth_class, 10)
        assertion.assert_(obj.meth_static, 10)
        assertion.assert_(MethodTest.meth_class, 10)
        assertion.assert_(MethodTest.meth_static, 10)
