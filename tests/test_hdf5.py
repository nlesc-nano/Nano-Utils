from __future__ import annotations

import copy
import pickle
import weakref
from pathlib import Path
from typing import TYPE_CHECKING, Any
from collections.abc import Iterator, Callable, KeysView, ItemsView, ValuesView

import pytest
from assertionlib import assertion
from nanoutils import RecursiveKeysView, RecursiveValuesView, RecursiveItemsView
from nanoutils.hdf5_utils import H5PY_VERSION
from packaging.version import Version

try:
    import h5py
    H5PY_EX: None | Exception = None
except Exception as ex:
    H5PY_EX = ex

if TYPE_CHECKING:
    import _pytest

HDF5_FILE = Path('tests') / 'test_files' / 'test.hdf5'
RAISE_MAPPING = {
    "hash": hash,
    "pickle": pickle.dumps,
    "deepcopy": copy.deepcopy,
}


@pytest.mark.skipif(H5PY_EX is not None, reason=str(H5PY_EX))
class TestRecursiveKeys:
    @pytest.fixture(scope="class", autouse=True)
    def view(self, request: _pytest.fixtures.SubRequest) -> Iterator[RecursiveKeysView]:
        with h5py.File(HDF5_FILE, "r") as f:
            ret = RecursiveKeysView(f)
            assertion.is_(ret.mapping, f)
            yield ret

    def test_len(self, view: RecursiveKeysView) -> None:
        assertion.len_eq(view, 3)

    def test_contains(self, view: RecursiveKeysView) -> None:
        assertion.contains(view, "/dset1")
        assertion.contains(view, "/a/dset2")
        assertion.contains(view, "/a/b/dset3")
        assertion.contains(view, "/a", invert=True)

    def test_iter(self, view: RecursiveKeysView) -> None:
        ref = ["/a/b/dset3", "/a/dset2", "/dset1"]
        assertion.eq(list(view), ref)
        assertion.eq(view, set(ref))
        assertion.eq(list(view), ref[1:], invert=True)

    @pytest.mark.skipif(H5PY_VERSION < Version("3.5.0"), reason="Requires h5py >= 3.5.0")
    def test_reversed(self, view: RecursiveKeysView) -> None:
        ref = ["/dset1", "/a/dset2", "/a/b/dset3"]
        assertion.eq(list(reversed(view)), ref)

    @pytest.mark.skipif(H5PY_VERSION >= Version("3.5.0"), reason="Requires h5py < 3.5.0")
    def test_reversed_raise(self, view: RecursiveKeysView) -> None:
        with pytest.raises(TypeError):
            reversed(view)

    def test_superset(self, view: RecursiveKeysView) -> None:
        ref_set = {"/a/b/dset3", "/a/dset2", "/dset1"}
        ref_superset = {"/a/b/c/dset4", "/a/b/dset3", "/a/dset2", "/dset1"}
        ref_subset = {"/a/dset2", "/dset1"}

        assertion.ge(view, ref_subset)
        assertion.ge(view, ref_set)
        assertion.ge(view, ref_superset, invert=True)

        assertion.gt(view, ref_subset)
        assertion.gt(view, ref_set, invert=True)
        assertion.gt(view, ref_superset, invert=True)

    def test_subset(self, view: RecursiveKeysView) -> None:
        ref_set = {"/a/b/dset3", "/a/dset2", "/dset1"}
        ref_superset = {"/a/b/c/dset4", "/a/b/dset3", "/a/dset2", "/dset1"}
        ref_subset = {"/a/dset2", "/dset1"}

        assertion.le(view, ref_subset, invert=True)
        assertion.le(view, ref_set)
        assertion.le(view, ref_superset)

        assertion.lt(view, ref_subset, invert=True)
        assertion.lt(view, ref_set, invert=True)
        assertion.lt(view, ref_superset)

    def test_union(self, view: RecursiveKeysView) -> None:
        ref_set = {"/a/b/dset3", "/a/dset2", "/dset1", 1, 2}
        assertion.eq(view | {1, 2}, ref_set)
        assertion.eq({1, 2} | view, ref_set)

    def test_intersection(self, view: RecursiveKeysView) -> None:
        ref_set = {"/a/b/dset3", "/a/dset2"}
        assertion.eq(view & ref_set, ref_set)
        assertion.eq(ref_set & view, ref_set)

    def test_isdisjoint(self, view: RecursiveKeysView) -> None:
        assertion.isdisjoint(view, {1})
        assertion.isdisjoint(view, {"/dset1"}, invert=True)

    def test_difference(self, view: RecursiveKeysView) -> None:
        ref_set = {"/a/b/dset3", "/a/dset2"}
        assertion.eq(view - {"/dset1"}, ref_set)
        assertion.eq({"/dset1"} - view, set())

    def test_symmetric_difference(self, view: RecursiveKeysView) -> None:
        ref_set = {"/a/b/dset3", "/a/dset2"}
        assertion.eq(view ^ {"/dset1"}, ref_set)
        assertion.eq({"/dset1"} ^ view, ref_set)

    @pytest.mark.parametrize("func", RAISE_MAPPING.values(), ids=RAISE_MAPPING.keys())
    def test_raise(self, view: RecursiveKeysView, func: Callable[[Any], object]) -> None:
        with pytest.raises(TypeError):
            func(view)

    @pytest.mark.parametrize("obj", [[1], {1: 1}], ids=["list", "dict"])
    def test_init(self, view: RecursiveKeysView, obj: Any) -> None:
        with pytest.raises(TypeError):
            RecursiveKeysView(obj)

    def test_weakref(self, view: RecursiveKeysView) -> None:
        assertion.eq(view, weakref.ref(view)())

    def test_superclass(self, view: RecursiveKeysView) -> None:
        assertion.isinstance(view, KeysView)

    def test_mapping(self, view: RecursiveKeysView) -> None:
        assertion.isinstance(view.mapping, h5py.Group)

    def test_eq(self, view: RecursiveKeysView) -> None:
        with h5py.File(view.mapping.filename) as f:
            view2 = RecursiveKeysView(f)
            assertion.eq(view, view2)
        assertion.ne(view, None)


@pytest.mark.skipif(H5PY_EX is not None, reason=str(H5PY_EX))
class TestRecursiveValues:
    @pytest.fixture(scope="class", autouse=True)
    def view(self, request: _pytest.fixtures.SubRequest) -> Iterator[RecursiveValuesView]:
        with h5py.File(HDF5_FILE, "r") as f:
            ret = RecursiveValuesView(f)
            assertion.is_(ret.mapping, f)
            yield ret

    def test_len(self, view: RecursiveValuesView) -> None:
        assertion.len_eq(view, 3)

    def test_contains(self, view: RecursiveValuesView) -> None:
        f = view.mapping
        assertion.contains(view, f["/dset1"])
        assertion.contains(view, f["/a/dset2"])
        assertion.contains(view, f["/a/b/dset3"])

    def test_iter(self, view: RecursiveValuesView) -> None:
        f = view.mapping
        ref = [f["/a/b/dset3"], f["/a/dset2"], f["/dset1"]]
        assertion.eq(list(view), ref)
        assertion.eq(list(view), ref[1:], invert=True)

    @pytest.mark.skipif(H5PY_VERSION < Version("3.5.0"), reason="Requires h5py >= 3.5.0")
    def test_reversed(self, view: RecursiveValuesView) -> None:
        f = view.mapping
        ref = [f["/dset1"], f["/a/dset2"], f["/a/b/dset3"]]
        assertion.eq(list(reversed(view)), ref)

    @pytest.mark.skipif(H5PY_VERSION >= Version("3.5.0"), reason="Requires h5py < 3.5.0")
    def test_reversed_raise(self, view: RecursiveValuesView) -> None:
        with pytest.raises(TypeError):
            reversed(view)

    @pytest.mark.parametrize("func", RAISE_MAPPING.values(), ids=RAISE_MAPPING.keys())
    def test_raise(self, view: RecursiveValuesView, func: Callable[[Any], object]) -> None:
        with pytest.raises(TypeError):
            func(view)

    @pytest.mark.parametrize("obj", [[1], {1: 1}], ids=["list", "dict"])
    def test_init(self, view: RecursiveValuesView, obj: Any) -> None:
        with pytest.raises(TypeError):
            RecursiveKeysView(obj)

    def test_weakref(self, view: RecursiveValuesView) -> None:
        assertion.eq(view, weakref.ref(view)())

    def test_superclass(self, view: RecursiveValuesView) -> None:
        assertion.isinstance(view, ValuesView)

    def test_mapping(self, view: RecursiveValuesView) -> None:
        assertion.isinstance(view.mapping, h5py.Group)

    def test_eq(self, view: RecursiveValuesView) -> None:
        with h5py.File(view.mapping.filename) as f:
            view2 = RecursiveValuesView(f)
            assertion.eq(view, view2)
        assertion.ne(view, None)


@pytest.mark.skipif(H5PY_EX is not None, reason=str(H5PY_EX))
class TestRecursiveItems:
    @pytest.fixture(scope="class", autouse=True)
    def view(self, request: _pytest.fixtures.SubRequest) -> Iterator[RecursiveItemsView]:
        with h5py.File(HDF5_FILE, "r") as f:
            ret = RecursiveItemsView(f)
            assertion.is_(ret.mapping, f)
            yield ret

    def test_len(self, view: RecursiveItemsView) -> None:
        assertion.len_eq(view, 3)

    def test_contains(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        assertion.contains(view, ("/dset1", f["/dset1"]))
        assertion.contains(view, ("/a/dset2", f["/a/dset2"]))
        assertion.contains(view, ("/a/b/dset3", f["/a/b/dset3"]))
        assertion.contains(view, "/a", invert=True)

    def test_iter(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref = [
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
            ("/dset1", f["/dset1"]),
        ]
        assertion.eq(list(view), ref)
        assertion.eq(view, set(ref))
        assertion.eq(list(view), ref[1:], invert=True)

    @pytest.mark.skipif(H5PY_VERSION < Version("3.5.0"), reason="Requires h5py >= 3.5.0")
    def test_reversed(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref = [
            ("/dset1", f["/dset1"]),
            ("/a/dset2",  f["/a/dset2"]),
            ("/a/b/dset3", f["/a/b/dset3"]),
        ]
        assertion.eq(list(reversed(view)), ref)

    @pytest.mark.skipif(H5PY_VERSION >= Version("3.5.0"), reason="Requires h5py < 3.5.0")
    def test_reversed_raise(self, view: RecursiveItemsView) -> None:
        with pytest.raises(TypeError):
            reversed(view)

    def test_superset(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref_set = {
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
            ("/dset1", f["/dset1"]),
        }
        ref_superset = ref_set | {("/a/b/c/dset4", 1)}
        ref_subset = ref_set - {("/a/b/dset3", f["/a/b/dset3"])}

        assertion.ge(view, ref_subset)
        assertion.ge(view, ref_set)
        assertion.ge(view, ref_superset, invert=True)

        assertion.gt(view, ref_subset)
        assertion.gt(view, ref_set, invert=True)
        assertion.gt(view, ref_superset, invert=True)

    def test_subset(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref_set = {
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
            ("/dset1", f["/dset1"]),
        }
        ref_superset = ref_set | {("/a/b/c/dset4", 1)}
        ref_subset = ref_set - {("/a/b/dset3", f["/a/b/dset3"])}

        assertion.le(view, ref_subset, invert=True)
        assertion.le(view, ref_set)
        assertion.le(view, ref_superset)

        assertion.lt(view, ref_subset, invert=True)
        assertion.lt(view, ref_set, invert=True)
        assertion.lt(view, ref_superset)

    def test_union(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref_set = {
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
            ("/dset1", f["/dset1"]),
            1,
            2,
        }
        assertion.eq(view | {1, 2}, ref_set)
        assertion.eq({1, 2} | view, ref_set)

    def test_intersection(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref_set = {
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
        }
        assertion.eq(view & ref_set, ref_set)
        assertion.eq(ref_set & view, ref_set)

    def test_isdisjoint(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        assertion.isdisjoint(view, {1})
        assertion.isdisjoint(view, {("/dset1", f["/dset1"])}, invert=True)

    def test_difference(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref_set = {
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
        }
        assertion.eq(view - {("/dset1", f["/dset1"])}, ref_set)
        assertion.eq({("/dset1", f["/dset1"])} - view, set())

    def test_symmetric_difference(self, view: RecursiveItemsView) -> None:
        f = view.mapping
        ref_set = {
            ("/a/b/dset3", f["/a/b/dset3"]),
            ("/a/dset2",  f["/a/dset2"]),
        }
        assertion.eq(view ^ {("/dset1", f["/dset1"])}, ref_set)
        assertion.eq({("/dset1", f["/dset1"])} ^ view, ref_set)

    @pytest.mark.parametrize("func", RAISE_MAPPING.values(), ids=RAISE_MAPPING.keys())
    def test_raise(self, view: RecursiveItemsView, func: Callable[[Any], object]) -> None:
        with pytest.raises(TypeError):
            func(view)

    @pytest.mark.parametrize("obj", [[1], {1: 1}], ids=["list", "dict"])
    def test_init(self, view: RecursiveItemsView, obj: Any) -> None:
        with pytest.raises(TypeError):
            RecursiveItemsView(obj)

    def test_weakref(self, view: RecursiveItemsView) -> None:
        assertion.eq(view, weakref.ref(view)())

    def test_superclass(self, view: RecursiveItemsView) -> None:
        assertion.isinstance(view, ItemsView)

    def test_mapping(self, view: RecursiveItemsView) -> None:
        assertion.isinstance(view.mapping, h5py.Group)

    def test_eq(self, view: RecursiveItemsView) -> None:
        with h5py.File(view.mapping.filename) as f:
            view2 = RecursiveItemsView(f)
            assertion.eq(view, view2)
        assertion.ne(view, None)
