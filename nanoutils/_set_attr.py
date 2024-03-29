"""A private module for containing the :class:`nanoutils.SetAttr` class.

Notes
-----
:class:`~nanoutils.SetAttr` should be imported from
either :mod:`nanoutils` or :mod:`nanoutils.utils`.

"""

import reprlib
from types import TracebackType
from typing import Generic, TypeVar, NoReturn, Dict, Any, Optional, Type, List
from threading import RLock

__all__: List[str] = []

_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_ST = TypeVar('_ST', bound='SetAttr[Any, Any]')


class SetAttr(Generic[_T1, _T2]):
    """A context manager for temporarily changing an attribute's value.

    The :class:`SetAttr` context manager is thread-safe, reusable and reentrant.

    Warnings
    --------
    Note that while :meth:`SetAttr.__enter__` and :meth:`SetAttr.__exit__` are thread-safe,
    the same does *not* hold for :meth:`SetAttr.__init__`.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import SetAttr

        >>> class Test:
        ...     a = False

        >>> print(Test.a)
        False

        >>> set_attr = SetAttr(Test, 'a', True)
        >>> with set_attr:
        ...     print(Test.a)
        True

    """

    __slots__ = ('__weakref__', '_obj', '_name', '_value', '_value_old', '_lock', '_hash')

    @property
    def obj(self) -> _T1:
        """:class:`object`: Get the to-be modified object."""
        return self._obj

    @property
    def name(self) -> str:
        """:class:`str`: Get the name of the to-be modified attribute."""
        return self._name

    @property
    def value(self) -> _T2:
        """:class:`object`: Get the value to-be assigned to the :attr:`name` attribute of :attr:`SetAttr.obj`."""  # noqa: E501
        return self._value

    @property
    def attr(self) -> _T2:
        """:class:`object`: Get or set the :attr:`~SetAttr.name` attribute of :attr:`SetAttr.obj`."""  # noqa: E501
        return getattr(self.obj, self.name)  # type: ignore

    @attr.setter
    def attr(self, value: _T2) -> None:
        with self._lock:
            setattr(self.obj, self.name, value)

    def __init__(self, obj: _T1, name: str, value: _T2) -> None:
        """Initialize the :class:`SetAttr` context manager.

        Parameters
        ----------
        obj : :class:`object`
            The to-be modified object.
            See :attr:`SetAttr.obj`.
        name : :class:`str`
            The name of the to-be modified attribute.
            See :attr:`SetAttr.name`.
        value : :class:`object`
            The value to-be assigned to the **name** attribute of **obj**.
            See :attr:`SetAttr.value`.


        :rtype: :data:`None`

        """
        self._obj = obj
        self._name = name
        self._value = value

        self._value_old = self.attr
        self._lock = RLock()

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        """Implement :class:`str(self)<str>` and :func:`repr(self)<repr>`."""
        obj = object.__repr__(self.obj)
        value = reprlib.repr(self.value)
        return f'{self.__class__.__name__}(obj={obj}, name={self.name!r}, value={value})'

    def __eq__(self, value: object) -> bool:
        """Implement :meth:`self == value<object.__eq__>`."""
        if type(self) is not type(value):
            return False
        return self.obj is value.obj and self.name == value.name and self.value == value.value  # type: ignore  # noqa: E501

    def __reduce__(self) -> NoReturn:
        """A helper for :mod:`pickle`.

        Warnings
        --------
        Unsupported operation, raises a :exc:`TypeError`.

        """
        raise TypeError(f"can't pickle {self.__class__.__name__} objects")

    def __copy__(self: _ST) -> _ST:
        """Implement :func:`copy.copy(self)<copy.copy>`."""
        return self

    def __deepcopy__(self: _ST, memo: Optional[Dict[int, Any]] = None) -> _ST:
        """Implement :func:`copy.deepcopy(self, memo=memo)<copy.deepcopy>`."""
        return self

    def __hash__(self) -> int:
        """Implement :func:`hash(self)<hash>`.

        Warnings
        --------
        A :exc:`TypeError` will be raised if :attr:`SetAttr.value` is not hashable.

        """
        try:
            return self._hash
        except AttributeError:
            args = (type(self), (id(self.obj), self.name, self.value))
            self._hash: int = hash(args)
            return self._hash

    def __enter__(self) -> None:
        """Enter the context manager, modify :attr:`SetAttr.obj`."""
        self.attr = self.value

    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        """Exit the context manager, restore :attr:`SetAttr.obj`."""
        self.attr = self._value_old
