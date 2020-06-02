"""A module with :mod:`schema`-related utility functions.

See Also
--------
.. image:: https://badge.fury.io/py/schema.svg
    :target: https://badge.fury.io/py/schema

**schema** is a library for validating Python data structures,
such as those obtained from config-files, forms,
external services or command-line parsing, converted from JSON/YAML
(or something else) to Python data-types.


Index
-----
.. currentmodule:: nanoutils
.. autosummary::
    {autosummary}

API
---
{autofunction}

"""

import inspect
import warnings
from typing import TypeVar, SupportsFloat, Callable, Union, overload, Generic, Tuple
from numbers import Integral

from .typing_utils import Literal
from .utils import PartialPrepend, get_importable, construct_api_doc

__all__ = ['Default', 'Formatter', 'supports_float', 'supports_int',
           'isinstance_factory', 'issubclass_factory', 'import_factory']

T = TypeVar('T')


@overload
def supports_float(value: SupportsFloat) -> Literal[True]: ...
@overload
def supports_float(value: object) -> bool: ...
def supports_float(value):  # noqa: E302
    """Check if a float-like object has been passed (:class:`~typing.SupportsFloat`)."""
    try:
        float(value)
        return True
    except Exception:
        return False


@overload
def supports_int(value: Union[int, Integral]) -> Literal[True]: ...
@overload
def supports_int(value: object) -> bool: ...
def supports_int(value):  # noqa: E302
    """Check if an int-like object has been passed (:class:`~typing.SupportsInt`)."""
    # floats that can be exactly represented by an integer are also fine
    try:
        int(value)
        return float(value).is_integer()
    except Exception:
        return False


class Default(Generic[T]):
    """A validation class akin to the likes of :class:`schemas.Use`.

    Upon executing :meth:`Default.validate` returns the stored :attr:`~Default.value`.
    If :attr:`~Default.call` is ``True`` and the value is a callable,
    then it is called before its return.

    Examples
    --------
    .. code:: python

        >>> from schema import Schema

        >>> schema1 = Schema(int, Default(True))
        >>> schema1.validate(1)
        True

        >>> schema2 = Schema(int, Default(dict))
        >>> schema2.validate(1)
        {}

        >>> schema3 = Schema(int, Default(dict, call=False))
        >>> schema3.validate(1)
        <class 'dict'>


    Attributes
    ----------
    value : :class:`object`
        The to-be return value for when :meth:`Default.validate` is called.
        If :attr:`Default.call` is ``True`` then the value is called
        (if possible) before its return.

    call : :class:`bool`
        Whether to call :attr:`Default.value` before its return (if possible) or not.

    """

    value: T
    call: bool

    def __init__(self, value: T, call: bool = True) -> None:
        """Initialize an instance."""
        self.value = value
        self.call = call

    def __repr__(self) -> str:
        """Implement :code:`str(self)` and :code:`repr(self)`."""
        return f'{self.__class__.__name__}({self.value!r}, call={self.call!r})'

    def validate(self, data: object) -> T:
        """Validate the passed **data**."""
        if self.call and callable(self.value):
            return self.value()
        else:
            return self.value


class Formatter(str):
    """A :class:`str` subclass used for creating :mod:`schema` error messages."""

    def __init__(self, msg: str):
        """Initialize an instance."""
        self._msg: str = msg

    def __repr__(self) -> str:
        """Implement :code:`str(self)` and :code:`repr(self)`."""
        return f'{self.__class__.__name__}(msg={self._msg!r})'

    def format(self, obj: object) -> str:  # type: ignore
        """Return a formatted version of :attr:`Formatter._msg`."""
        name = self._msg.split("'", maxsplit=2)[1]
        name_ = name or 'value'
        try:
            return self._msg.format(name=name_, value=obj, type=obj.__class__.__name__)
        except Exception as ex:
            err = RuntimeWarning(ex)
            err.__cause__ = ex
            warnings.warn(err)
            return repr(obj)

    @property
    def __mod__(self):  # type: ignore
        """Get :meth:`Formatter.format`."""
        return self.format


ClassOrTuple = Union[type, Tuple[type, ...]]

PO = inspect.Parameter.POSITIONAL_ONLY
POK = inspect.Parameter.POSITIONAL_OR_KEYWORD


def isinstance_factory(class_or_tuple: ClassOrTuple) -> Callable[[object], bool]:
    """Return a function which checks if the passed object is an instance of **class_or_tuple**.

    Parameters
    ----------
    class_or_tuple : :class:`type` or :class:`Tuple[type, ...]<typing.Tuple>`
        A type object or tuple of type objects.

    Returns
    -------
    :data:`Callable[[object], bool]<typing.Callable>`
        A function which asserts the passed object is an instance of **class_or_tuple**.

    See Also
    --------
    :func:`isinstance`
        Return whether an object is an instance of a class or of a subclass thereof.

    """
    try:
        isinstance('bob', class_or_tuple)
    except TypeError as ex:
        raise TypeError("'class_or_tuple' expected a type or tuple of types; "  # type: ignore
                        f"observed type: {class_or_tuple.__class__.__name__!r}") from ex

    if isinstance(class_or_tuple, type):
        cls_str = class_or_tuple.__name__
    else:
        cls_str = f'({", ".join(cls.__name__ for cls in class_or_tuple)})'

    ret = PartialPrepend(isinstance, class_or_tuple)
    ret.__name__ = ret.func.__name__  # type: ignore
    ret.__qualname__ = ret.func.__qualname__  # type: ignore
    ret.__module__ = __name__
    ret.__doc__ = f'Return :code:`isinstance(obj, {cls_str})`.'
    ret.__signature__ = inspect.Signature(  # type: ignore
        parameters=[inspect.Parameter('obj', PO, annotation=object)],
        return_annotation=bool
    )
    return ret


def issubclass_factory(class_or_tuple: ClassOrTuple) -> Callable[[type], bool]:
    """Return a function which checks if the passed class is a subclass of **class_or_tuple**.


    Parameters
    ----------
    class_or_tuple : :class:`type` or :class:`Tuple[type, ...]<typing.Tuple>`
        A type object or tuple of type objects.

    Returns
    -------
    :data:`Callable[[object], bool]<typing.Callable>`
        A function which asserts the passed type is a subclass of **class_or_tuple**.

    See Also
    --------
    :func:`issubclass`
        Return whether **cls** is a derived from another class or is the same class.

    """
    try:
        issubclass(int, class_or_tuple)
    except TypeError as ex:
        raise TypeError("'class_or_tuple' expected a type or tuple of types; "  # type: ignore
                        f"observed type: {class_or_tuple.__class__.__name__!r}") from ex

    if isinstance(class_or_tuple, type):
        cls_str = class_or_tuple.__name__
    else:
        cls_str = f'({", ".join(cls.__name__ for cls in class_or_tuple)})'

    ret = PartialPrepend(issubclass, class_or_tuple)
    ret.__name__ = ret.func.__name__  # type: ignore
    ret.__qualname__ = ret.func.__qualname__  # type: ignore
    ret.__module__ = __name__
    ret.__doc__ = f'Return :code:`isinstance(obj, {cls_str})`.'
    ret.__signature__ = inspect.Signature(  # type: ignore
        parameters=[inspect.Parameter('cls', PO, annotation=type)],
        return_annotation=bool
    )
    return ret


def import_factory(validate: Callable[[T], bool]) -> Callable[[str], T]:
    """Return a function which calls :func:`nanoutils.get_importable` with the **validate** argument.

    Parameters
    ----------
    validate : :data:`Callable[[T], bool]<typing.Callable>`
        A callable used for validating the passed object.

    Returns
    -------
    :data:`Callable[[str], T]<typing.Callable>`
        A function for importing the passed object and validating it using **validate**.

    See Also
    --------
    :func:`nanoutils.get_importable`
        Import an object and, optionally, validate it using **validate**.

    """  # noqa: E501
    if not callable(validate):
        raise TypeError("'validate' expected a callable; observed type: "
                        f"{validate.__class__.__name__!r}")

    try:
        val_name = validate.__qualname__
    except AttributeError:
        val_name = repr(validate)

    ret = PartialPrepend(get_importable, validate=validate)
    ret.__name__ = ret.func.__name__  # type: ignore
    ret.__qualname__ = ret.func.__qualname__  # type: ignore
    ret.__module__ = __name__
    ret.__doc__ = f'Return :code:`nanoutils.get_importable(string, validate={val_name})`.'
    ret.__signature__ = inspect.Signature(  # type: ignore
        parameters=[inspect.Parameter('string', POK, annotation=str)],
        return_annotation=object
    )
    return ret


__doc__ = construct_api_doc(globals())
