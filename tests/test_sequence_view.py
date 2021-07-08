from __future__ import annotations

import copy
import pickle
import weakref
from typing import Sequence, TYPE_CHECKING

import pytest
from assertionlib import assertion
from nanoutils import SequenceView

if TYPE_CHECKING:
    import _pytest  # noqa: F401

SEQ_DICT: dict[str, Sequence[int]] = {
    "list": [0, 1, 2, 3, 4, 5],
    "tuple": (0, 1, 2, 3, 4, 5),
    "bytes": b"\x00\x01\x02\x03\x04\x05",
    "bytearray": bytearray(b"\x00\x01\x02\x03\x04\x05"),
    "range": range(6),
}


@pytest.mark.parametrize(
    "seq,view", [(v, SequenceView(v)) for v in SEQ_DICT.values()],
    ids=SEQ_DICT.keys(),
)
class TestSequenceView:
    """Tests for :class:`nanoutils.SequenceView`."""

    def test_hash(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.eq(hash(view), hash(SequenceView(seq)))
        assertion.eq(hash(view), hash(SequenceView(view)))

    def test_reduce(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        with pytest.raises(TypeError):
            pickle.dumps(view)

    def test_copy(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.is_(view, copy.copy(view))

    def test_deepcopy(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.is_(view, copy.deepcopy(view))

    def test_weakref(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.is_(view, weakref.ref(view)())

    @pytest.mark.parametrize("i", range(0, 6, 2))
    def test_getitem_int(self, seq: Sequence[int], view: SequenceView[int], i: int) -> None:
        assertion.eq(view[i], seq[i])
        assertion.isinstance(view[i], type(seq[i]))

    @pytest.mark.parametrize("i", range(1, 6, 2))
    def test_getitem_slice(self, seq: Sequence[int], view: SequenceView[int], i: int) -> None:
        assertion.eq(view[:i], seq[:i])
        assertion.eq(view[i:], seq[i:])
        assertion.eq(view[::i], seq[::i])
        assertion.isinstance(view[:], SequenceView)

    @pytest.mark.parametrize("i", range(0, 6, 2))
    def test_index(self, seq: Sequence[int], view: SequenceView[int], i: int) -> None:
        assertion.eq(view.index(i), seq.index(i))

    @pytest.mark.parametrize("i", range(0, 6, 2))
    def test_count(self, seq: Sequence[int], view: SequenceView[int], i: int) -> None:
        assertion.eq(view.count(i), seq.count(i))

    def test_len(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.eq(len(view), len(seq))

    @pytest.mark.parametrize("i", range(0, 6, 2))
    def test_contains(self, seq: Sequence[int], view: SequenceView[int], i: int) -> None:
        assertion.contains(view, i)
        assertion.eq(i in view, i in seq)

    def test_iter(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.eq(list(iter(view)), list(iter(seq)))

    def test_reversed(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.eq(list(reversed(view)), list(reversed(seq)))

    def test_repr(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.contains(repr(view), SequenceView.__name__)
        assertion.contains(repr(view), repr(seq))

    def test_eq(self, seq: Sequence[int], view: SequenceView[int]) -> None:
        assertion.eq(seq, view)
        assertion.eq(view, view)
        assertion.eq(seq, seq)
        assertion.eq(view, SequenceView(view))
        assertion.eq(view, SequenceView(seq))
