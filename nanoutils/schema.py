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

from __future__ import annotations

import inspect
import warnings
from typing import TypeVar, SupportsFloat, Callable, overload, Generic, Tuple
from numbers import Integral

from .typing_utils import Literal
from .utils import PartialPrepend, get_importable, construct_api_doc, get_func_name

__all__ = ['Default', 'Formatter', 'supports_float', 'supports_int',
           'isinstance_factory', 'issubclass_factory', 'import_factory']

_T = TypeVar('_T')


@overload
def supports_float(value: SupportsFloat) -> Literal[True]:
    ...
@overload  # noqa: E302
def supports_float(value: object) -> bool:
    ...
def supports_float(value: object) -> bool:  # noqa: E302
    """Check if a float-like object has been passed (:class:`~typing.SupportsFloat`).

    Examples
    --------
    .. code:: python

        >>> from nanoutils import supports_float

        >>> supports_float(1.0)
        True

        >>> supports_float(1)
        True

        >>> supports_float('1.0')
        True

        >>> supports_float('not a float')
        False

    Parameters
    ----------
    value : :class:`object`
        The to-be evaluated object.

    Returns
    -------
    :class:`bool`
        Whether or not the passed **value** is float-like or not.

    """
    try:
        float(value)  # type: ignore
        return True
    except Exception:
        return False


@overload
def supports_int(value: int | Integral) -> Literal[True]:
    ...
@overload  # noqa: E302
def supports_int(value: object) -> bool:
    ...
def supports_int(value: object) -> bool:  # noqa: E302
    """Check if an int-like object has been passed (:class:`~typing.SupportsInt`).

    Examples
    --------
    .. code:: python

        >>> from nanoutils import supports_int

        >>> supports_int(1.0)
        True

        >>> supports_int(1.5)
        False

        >>> supports_int(1)
        True

        >>> supports_int('1')
        True

        >>> supports_int('not a int')
        False

    Parameters
    ----------
    value : :class:`object`
        The to-be evaluated object.

    Returns
    -------
    :class:`bool`
        Whether or not the passed **value** is int-like or not.

    """
    # floats that can be exactly represented by an integer are also fine
    try:
        int(value)  # type: ignore
        return float(value).is_integer()  # type: ignore
    except Exception:
        return False


class Default(Generic[_T]):
    """A validation class akin to the likes of :class:`schemas.Use`.

    Upon executing :meth:`Default.validate` returns the stored :attr:`~Default.value`.
    If :attr:`~.Default.call` is ``True`` and the value is a callable,
    then it is called before its return.

    Examples
    --------
    .. code:: python

        >>> from schema import Schema, And
        >>> from nanoutils import Default

        >>> schema1 = Schema(And(int, Default(True)))
        >>> schema1.validate(1)
        True

        >>> schema2 = Schema(And(int, Default(dict)))
        >>> schema2.validate(1)
        {}

        >>> schema3 = Schema(And(int, Default(dict, call=False)))
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

    value: _T
    call: bool

    def __init__(self, value: _T, call: bool = True) -> None:
        """Initialize an instance."""
        self.value = value
        self.call = call

    def __repr__(self) -> str:
        """Implement :code:`str(self)` and :code:`repr(self)`."""
        return f'{self.__class__.__name__}({self.value!r}, call={self.call!r})'

    def validate(self, *args: object, **kwargs: object) -> _T:
        r"""Validate the passed **data**.

        Parameters
        ----------
        \*args/\**kwargs
            Variadic (keyword) arguments to ensure signature compatibility.
            Supplied values will not be used.

        Returns
        -------
        :class:`object`
            Return :attr:`Default.value`.
            The to-be returned value will be called if
            it is a callable and :attr:`Default.call` is :data:`True`.

        """
        if self.call and callable(self.value):
            return self.value()  # type: ignore
        else:
            return self.value


class Formatter(str):
    r"""A :class:`str` subclass used for creating :mod:`schema` error messages.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import Formatter

        >>> string = Formatter("{name}: {type} = {value}")
        >>> string.format(1)
        'value: int = 1'

    """

    def __init__(self, msg: str) -> None:
        """Initialize an instance."""
        self._msg: str = msg

    def __repr__(self) -> str:
        """Implement :code:`str(self)` and :code:`repr(self)`."""
        return f'{self.__class__.__name__}(msg={self._msg!r})'

    def format(self, obj: object) -> str:  # type: ignore
        r"""Return a formatted version of :attr:`Formatter._msg`.

        Parameters
        ----------
        obj : :class:`object`
            The to-be formatted object.

        Returns
        -------
        :class:`str`
            A formatted string.

        """
        try:
            name = self._msg.split("'", maxsplit=2)[1]
        except IndexError:
            name = ''
        name_ = name or 'value'

        try:
            return self._msg.format(name=name_, value=obj, type=obj.__class__.__name__)
        except Exception as ex:
            err = RuntimeWarning(ex)
            err.__cause__ = ex
            warnings.warn(err)
            return repr(obj)

    @property
    def __mod__(self):
        """Get :meth:`Formatter.format`."""
        return self.format


_PO = inspect.Parameter.POSITIONAL_ONLY
_POK = inspect.Parameter.POSITIONAL_OR_KEYWORD


def isinstance_factory(
    class_or_tuple: type | Tuple[type, ...],
    module: str = __name__,
) -> Callable[[object], bool]:
    """Return a function which checks if the passed object is an instance of **class_or_tuple**.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import isinstance_factory

        >>> func = isinstance_factory(int)

        >>> func(1)  # isinstance(1, int)
        True

        >>> func(1.0)  # isinstance(1.0, int)
        False

    Parameters
    ----------
    class_or_tuple : :class:`type` or :data:`Tuple[type, ...]<typing.Tuple>`
        A type object or tuple of type objects.
    module : :class:`str`
        The :attr:`~definition.__module__` of the to-be returned function.

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
        raise TypeError("'class_or_tuple' expected a type or tuple of types; "
                        f"observed type: {class_or_tuple.__class__.__name__!r}") from ex

    if isinstance(class_or_tuple, type):
        cls_str = class_or_tuple.__name__
    else:
        cls_str = f'({", ".join(cls.__name__ for cls in class_or_tuple)})'

    ret = PartialPrepend(isinstance, class_or_tuple)
    ret.__name__ = ret.func.__name__  # type: ignore
    ret.__qualname__ = ret.func.__qualname__  # type: ignore
    ret.__module__ = module
    ret.__doc__ = f'Return :code:`isinstance(obj, {cls_str})`.'
    ret.__signature__ = inspect.Signature(  # type: ignore
        parameters=[inspect.Parameter('obj', _PO, annotation=object)],
        return_annotation=bool
    )
    return ret


def issubclass_factory(
    class_or_tuple: type | Tuple[type, ...],
    module: str = __name__,
) -> Callable[[type], bool]:
    """Return a function which checks if the passed class is a subclass of **class_or_tuple**.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import issubclass_factory

        >>> func = issubclass_factory(int)

        >>> func(bool)  # issubclass(bool, int)
        True

        >>> func(float)  # issubclass(float, int)
        False

    Parameters
    ----------
    class_or_tuple : :class:`type` or :data:`Tuple[type, ...]<typing.Tuple>`
        A type object or tuple of type objects.
    module : :class:`str`
        The :attr:`~definition.__module__` of the to-be returned function.

    Returns
    -------
    :data:`Callable[[type], bool]<typing.Callable>`
        A function which asserts the passed type is a subclass of **class_or_tuple**.

    See Also
    --------
    :func:`issubclass`
        Return whether **cls** is a derived from another class or is the same class.

    """
    try:
        issubclass(int, class_or_tuple)
    except TypeError as ex:
        raise TypeError("'class_or_tuple' expected a type or tuple of types; "
                        f"observed type: {class_or_tuple.__class__.__name__!r}") from ex

    if isinstance(class_or_tuple, type):
        cls_str = class_or_tuple.__name__
    else:
        cls_str = f'({", ".join(cls.__name__ for cls in class_or_tuple)})'

    ret = PartialPrepend(issubclass, class_or_tuple)
    ret.__name__ = ret.func.__name__  # type: ignore
    ret.__qualname__ = ret.func.__qualname__  # type: ignore
    ret.__module__ = module
    ret.__doc__ = f'Return :code:`isinstance(obj, {cls_str})`.'
    ret.__signature__ = inspect.Signature(  # type: ignore
        parameters=[inspect.Parameter('cls', _PO, annotation=type)],
        return_annotation=bool
    )
    return ret


def import_factory(
    validate: Callable[[_T], bool],
    module: str = __name__,
) -> Callable[[str], _T]:
    """Return a function which calls :func:`nanoutils.get_importable` with the **validate** argument.

    Examples
    --------
    .. code:: python

        >>> from inspect import isclass
        >>> from nanoutils import import_factory

        >>> func = import_factory(isclass)
        >>> func('builtins.dict')
        <class 'dict'>

        >>> func('builtins.len')
        Traceback (most recent call last):
          ...
        RuntimeError: Passing <built-in function len> to isclass() failed to return True

    Parameters
    ----------
    validate : :data:`Callable[[T], bool]<typing.Callable>`
        A callable used for validating the passed object.
    module : :class:`str`
        The :attr:`~definition.__module__` of the to-be returned function.

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

    val_name = get_func_name(validate, repr_fallback=True)

    ret = PartialPrepend(get_importable, validate=validate)
    name_fallback = f'{ret.func.__class__.__name__}(...)'

    ret.__name__: str = getattr(ret.func, '__name__', name_fallback)  # type: ignore
    ret.__qualname__: str = getattr(ret.func, '__qualname__', name_fallback)  # type: ignore
    ret.__module__ = module
    ret.__doc__ = f'Return :code:`nanoutils.get_importable(string, validate={val_name})`.'
    ret.__signature__ = inspect.Signature(  # type: ignore
        parameters=[inspect.Parameter('string', _POK, annotation=str)],
        return_annotation=object
    )
    return ret


__doc__ = construct_api_doc(globals())
