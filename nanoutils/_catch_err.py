"""A private module for containg the :class:`nanoutils.CatchErrors` class.

Notes
-----
:class:`~nanoutils.CatchErrors` should be imported from
either :mod:`nanoutils` or :mod:`nanoutils.utils`.

"""

from __future__ import annotations

import types
from typing import (
    TypeVar,
    Generic,
    Tuple,
    Type,
    List,
    cast,
    Iterable,
    Any,
    Callable,
)

from ._seq_view import SequenceView

_ET = TypeVar("_ET", bound=BaseException)
_ET2 = TypeVar("_ET2", bound=BaseException)

__all__ = ["CatchErrors"]


class CatchErrors(Generic[_ET]):
    """A re-usable context manager for catching and storing all exceptions of a given type.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import CatchErrors

        >>> context = CatchErrors(AssertionError)

        >>> for i in range(3):
        ...     with context as exc_view:
        ...         assert False, i  # doctest: +SKIP
        ...         print(exc_view)
        SequenceView([AssertionError(0)])
        SequenceView([AssertionError(0), AssertionError(1)])
        SequenceView([AssertionError(0), AssertionError(1), AssertionError(2)])

    See Also
    --------
    :class:`contextlib.suppress`
        Context manager to suppress specified exceptions.

    """  # noqa: E501

    __slots__ = ("__weakref__", "_exceptions", "_caught_exceptions")

    @property
    def exceptions(self) -> Tuple[Type[_ET], ...]:
        """Get the to-be caught exception types."""
        return self._exceptions

    @property
    def caught_exceptions(self) -> SequenceView[_ET]:
        """Get a read-only view of all caught exceptions."""
        return SequenceView(self._caught_exceptions)

    def __init__(self, *exceptions: Type[_ET]) -> None:
        r"""Initialize this instance.

        Parameters
        ----------
        \*exceptions : :class:`type[BaseException] <type>`
            The to-be caught exceptions.

        """
        self._exceptions = exceptions
        self._caught_exceptions: List[_ET] = []

    def clear(self) -> None:
        """Clear all caught exceptions."""
        self._caught_exceptions = []

    def __repr__(self) -> str:
        """Implement :func:`repr(self) <repr>`."""
        name = type(self).__name__
        args = ", ".join(i.__name__ for i in self.exceptions)
        return f"{name}({args})"

    @classmethod
    def _reconstruct(
        cls: Type["CatchErrors[Any]"],
        exc_types: Iterable[Type[_ET2]],
        exc_list: List[_ET2],
    ) -> "CatchErrors[_ET2]":
        """Construct a new :class:`CatchErrors` instance; see :meth:`__reduce__`."""
        self: CatchErrors[_ET2] = cls(*exc_types)
        self._caught_exceptions = exc_list
        return self

    def __reduce__(self) -> Tuple[
        Callable[[Iterable[Type[_ET2]], List[_ET2]], "CatchErrors[_ET2]"],
        Tuple[Tuple[Type[_ET], ...], List[_ET]],
    ]:
        """Helper method for :mod:`pickle`."""
        cls = type(self)
        return cls._reconstruct, (self.exceptions, self._caught_exceptions)

    def __enter__(self) -> SequenceView[_ET]:
        """Enter the context manager.

        Returns
        -------
        :class:`nanoutils.SequenceView`
            A read-only sequence view with all caught exceptions.

        """
        return self.caught_exceptions

    def __exit__(
        self,
        exctype: None | Type[BaseException] = None,
        excinst: None | BaseException = None,
        exctb: None | types.TracebackType = None,
    ) -> bool:
        """Exit the context manager.

        Update :attr:`caught_exceptions` if an appropriate exception is encountered.
        """
        if exctype is not None and issubclass(exctype, self.exceptions):
            self._caught_exceptions.append(cast(_ET, excinst))
            return True
        return False
