"""Tests for :class:`~nanoutil.LazyImporter`."""

from __future__ import annotations

import sys
import copy
import types
import pickle
import weakref
import textwrap
import subprocess
from itertools import chain
from typing import Any, Mapping, TYPE_CHECKING, no_type_check

import pytest
from assertionlib import assertion
from nanoutils import LazyImporter, MutableLazyImporter

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

IMPORTS = {
    "chain": "itertools",
    "product": "itertools",
    "Hashable": "collections.abc",
    "decode": "codecs",
    "dis": "pickletools",
}

LAZY_IMPORT = LazyImporter.from_name(__name__, IMPORTS)
MUTABLE_LAZY_IMPORT = MutableLazyImporter.from_name(__name__, IMPORTS)


def all_str(dct: Mapping[Any, Any]) -> TypeGuard[Mapping[str, str]]:
    """Check that all keys and values of **dct** are strings."""
    return all(isinstance(i, str) for i in chain.from_iterable(dct.items()))


@pytest.mark.parametrize("obj", [LAZY_IMPORT, MUTABLE_LAZY_IMPORT])
class TestLazyImporter:
    CODE = textwrap.dedent("""
        >>> import pytest
        >>> import sys
        >>> import nanoutils
        >>> from assertionlib import assertion

        >>> __getattr__ = nanoutils.{cls_name}(
        ...     module=nanoutils,
        ...     imports={imports},
        ... )

        >>> assertion.issubset(
        ...     set(__getattr__.imports.values()),
        ...     set(sys.modules.keys()),
        ...     invert=True,
        ... )

        >>> for name in __getattr__.imports.keys():
        ...     assertion.truth(__getattr__(name))
        ...     assertion.hasattr(__getattr__.module, name)

        >>> with pytest.raises(AttributeError):
        ...     __getattr__("bob")

        >>> for name in __getattr__.imports.keys():
        ...     assertion.is_(__getattr__(name), getattr(__getattr__.module, name))
    """).strip("\n")

    def test_hash(self, obj: LazyImporter) -> None:
        if type(obj) is MutableLazyImporter:
            assertion.assert_(hash, obj, exception=TypeError)
        else:
            assertion.assert_(hash, obj)
            assertion.assert_(hash, obj)

    def test_eq(self, obj: LazyImporter) -> None:
        assertion.eq(obj, obj)
        assertion.ne(obj, None)

        cls = type(obj)
        obj2 = cls(obj.module, {})
        assertion.ne(obj, obj2)

    def test_pickle(self, obj: LazyImporter) -> None:
        obj2 = pickle.loads(pickle.dumps(obj))
        assertion.eq(obj, obj2)

    def test_weakref(self, obj: LazyImporter) -> None:
        obj2 = weakref.ref(obj)()
        assertion.is_(obj, obj2)

    def test_copy(self, obj: LazyImporter) -> None:
        obj2 = copy.copy(obj)
        assertion.eq(obj, obj2)

        if type(obj) is MutableLazyImporter:
            assertion.is_not(obj, obj2)
            assertion.is_(obj.module, obj2.module)
            assertion.is_(obj.imports, obj2.imports)
        else:
            assertion.is_(obj, obj2)

    def test_deepcopy(self, obj: LazyImporter) -> None:
        obj2 = copy.deepcopy(obj)
        assertion.eq(obj, obj2)

        if type(obj) is MutableLazyImporter:
            assertion.is_not(obj, obj2)
            assertion.is_(obj.module, obj2.module)
            assertion.is_not(obj.imports, obj2.imports)
        else:
            assertion.is_(obj, obj2)

    def test_repr(self, obj: LazyImporter) -> None:
        assertion.assert_(str, obj)
        assertion.assert_(repr, obj)
        assertion.eq(str(obj), repr(obj))

        string = repr(obj)
        assertion.contains(string, type(obj).__name__)
        assertion.contains(string, obj.module.__name__)

    def test_attr(self, obj: LazyImporter) -> None:
        assertion.isinstance(obj.module, types.ModuleType)
        if type(obj) is MutableLazyImporter:
            assertion.isinstance(obj.imports, dict)
        else:
            assertion.isinstance(obj.imports, types.MappingProxyType)
        assertion.assert_(all_str, obj.imports)

    def test_cls_getitem(self, obj: LazyImporter) -> None:
        cls = type(obj)
        assertion.truth(cls[str])  # type: ignore[index]

    def test_call(self, obj: LazyImporter) -> None:
        code = self.CODE.format(
            cls_name=type(obj).__name__,
            module_name=obj.module.__name__,
            imports=obj.imports,
        ) + "\n"
        code_parsed = "\n".join((i[4:] if i else i) for i in code.split("\n"))

        p = subprocess.run([sys.executable, '-c', code_parsed], capture_output=True)
        if p.returncode:
            raise AssertionError(
                f"Non-zero return code: {p.returncode!r}\n\n{code}\n{p.stderr.decode()}"
            )

    def test_setattr(self, obj: LazyImporter) -> None:
        if type(obj) is not MutableLazyImporter:
            with pytest.raises(AttributeError):
                obj.imports = obj.imports  # type: ignore[misc]
        else:
            imports_old = obj.imports
            obj.imports = obj.imports
            assertion.eq(imports_old, obj.imports)
            assertion.is_not(imports_old, obj.imports)

    @no_type_check
    def test_init(self, obj: LazyImporter) -> None:
        cls = type(obj)
        with pytest.raises(TypeError):
            cls(1, {})
        with pytest.raises(TypeError):
            cls(obj.module, [1])

    @no_type_check
    def test_from_name(self, obj: LazyImporter) -> None:
        cls = type(obj)
        with pytest.raises(TypeError):
            cls.from_name(1, {})
        with pytest.raises(TypeError):
            cls.from_name(obj.module, [1])
        assertion.assert_(cls.from_name, "pickletools", {})


def test_mapping_protocol() -> None:
    if TYPE_CHECKING:
        from nanoutils._lazy_import import _MappingProtocol

        a: dict[str, str] = {"a": "a"}
        b: _MappingProtocol[str, str] = {"a": "a"}
        assert a == b
