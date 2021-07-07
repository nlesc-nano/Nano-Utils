"""A private module for containg the :class:`nanoutils.SequenceView` class.

Notes
-----
:class:`~nanoutils.SequenceView` should be imported from
either :mod:`nanoutils` or :mod:`nanoutils.utils`.

"""

from __future__ import annotations

import pprint
import textwrap
from typing import (
    Any,
    TypeVar,
    Sequence,
    NoReturn,
    overload,
    Iterator,
    Dict,
    ClassVar,
)

from .typing_utils import TypedDict

if sys.version_info >= (3, 8):
    class _PPrintDict(TypedDict, total=False):
        indent: int
        width: int
        depth: None | int
        compact: bool
        sort_dicts: bool
else:
    class _PPrintDict(TypedDict, total=False):
        indent: int
        width: int
        depth: None | int
        compact: bool

_T_co = TypeVar("_T_co", covariant=True)
_SVT = TypeVar("_SVT", bound="SequenceView[Any]")

__all__ = ["SequenceView"]


class SequenceView(Sequence[_T_co]):
    """A read-only view of an underlying :class:`~collections.abc.Sequence`.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import SequenceView

        >>> lst = [1, 2, 3]
        >>> view = SequenceView(lst)
        >>> print(view)
        SequenceView([1, 2, 3])

        >>> lst.append(4)
        >>> print(view)
        SequenceView([1, 2, 3, 4])

        >>> print(len(view))
        4

        >>> del view[0]
        Traceback (most recent call last):
            ...
        TypeError: 'SequenceView' object doesn't support item deletion

    """

    __slots__ = ("__weakref__", "_seq")

    #: A class variable containing a dictionary with keyword arguments for :func:`pprint.pformat`.
    pprint_kwargs: ClassVar[_PPrintDict] = NotImplemented

    def __init__(self, sequence: Sequence[_T_co]) -> None:
        r"""Initialize this instance.

        Parameters
        ----------
        sequence : :class:`~collections.abc.Sequence`
            The to-be wrapped sequence.

        """
        self._seq: Sequence[_T_co] = sequence

    def __init_subclass__(cls) -> None:
        """Attach a unique :attr:`~SequenceView.pprint_kwargs` dict to each subclass."""
        super().__init_subclass__()
        width = 80 - 1 - len(cls.__name__)
        if cls.pprint_kwargs is NotImplemented:
            dct: _PPrintDict = {"compact": True, "width": width}
            if sys.version_info >= (3, 8):
                dct["sort_dicts"] = False
        else:
            dct = cls.pprint_kwargs.copy()
            dct["width"] = width
        cls.pprint_kwargs = dct

    def __hash__(self) -> int:
        """Implement :func:`hash(sellf) <hash>`."""
        if isinstance(self._seq, SequenceView):
            # delegate to the underlying `SequenceView` instance
            return hash(self._seq)
        else:
            return id(self._seq)

    def __reduce__(self) -> NoReturn:
        """Helper method for :mod:`pickle`."""
        raise TypeError(f"cannot pickle {type(self).__name__!r} object")

    def __copy__(self: _SVT) -> _SVT:
        """Return a shallow copy of this instance."""
        return self  # `self` is immutable

    def __deepcopy__(self: _SVT, memo: None | Dict[int, Any] = None) -> _SVT:
        """Return a deep copy of this instance."""
        return self  # `self` is immutable

    @overload
    def __getitem__(self, key: int) -> _T_co:
        ...
    @overload  # noqa: E301
    def __getitem__(self: _SVT, key: slice) -> _SVT:
        ...
    def __getitem__(self: _SVT, key: int | slice) -> _SVT | _T_co:  # noqa: E301
        """Implement :meth:`self[key] <object.__getitem__>`."""
        if isinstance(key, slice):
            cls = type(self)
            return cls(self._seq[key])
        return self._seq[key]  # type: ignore[no-any-return]

    def index(
        self,
        value: Any,
        start: None | int = None,
        stop: None | int = None,
    ) -> int:
        """Return the first index of **value**."""
        args = []
        if start is not None:
            args.append(start)
        if stop is not None:
            args.append(stop)
        return self._seq.index(value, *args)

    def count(self, value: Any) -> int:
        """Return the number of times **value** occurs in the instance."""
        return self._seq.count(value)

    def __len__(self):
        """Implement :func:`len(self) <len>`."""
        return len(self._seq)

    def __contains__(self, x: object) -> bool:
        """Implement :meth:`x in self <object.__contains__>`."""
        return x in self._seq

    def __iter__(self) -> Iterator[_T_co]:
        """Implement :func:`iter(self) <iter>`."""
        return iter(self._seq)

    def __reversed__(self) -> Iterator[_T_co]:
        """Implement :func:`reversed(self) <reversed>`."""
        return reversed(self._seq)

    def __repr__(self) -> str:
        """Implement :func:`repr(self) <repr>`."""
        cls = type(self)
        name = cls.__name__
        offset = len(name) + 1

        seq = pprint.pformat(self._seq, **cls.pprint_kwargs)
        seq_indent = textwrap.indent(seq, " " * offset)[offset:]
        return f"{name}({seq_indent})"

    def __eq__(self, other: object) -> bool:
        """Implement :meth:`x == self <object.__eq__>`."""
        return self._seq == other


# Ensure that `__init_subclass__` is called not just for `SequenceView` subclasses,
# but also the superclass itself.
SequenceView.__init_subclass__()
