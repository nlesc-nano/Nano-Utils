"""General utility functions.

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

import re
import warnings
import importlib
from types import ModuleType
from functools import wraps
from typing import (
    List,
    Any,
    Tuple,
    Callable,
    TypeVar,
    Iterable,
    Dict,
    Container,
    Mapping,
    NamedTuple,
    NoReturn,
    MutableMapping,
    Collection,
    cast,
    overload
)

from .empty import EMPTY_CONTAINER
from ._partial import PartialPrepend
from ._set_attr import SetAttr
from ._seq_view import SequenceView
from ._catch_err import CatchErrors
from ._lazy_import import LazyImporter, MutableLazyImporter

__all__ = [
    'PartialPrepend',
    'SetAttr',
    'VersionInfo',
    'group_by_values',
    'get_importable',
    'construct_api_doc',
    'split_dict',
    'get_func_name',
    'set_docstring',
    'raise_if',
    'ignore_if',
    'SequenceView',
    'CatchErrors',
    'LazyImporter',
    'MutableLazyImporter',
]

_T = TypeVar('_T')
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')
_FT = TypeVar('_FT', bound=Callable[..., Any])


def get_func_name(
    func: Callable[..., Any],
    prepend_module: bool = False,
    repr_fallback: bool = False,
) -> str:
    """Extract and return the name of **func**.

    A total of three attempts are performed at retrieving the passed functions name:

    1. Return the functions qualified name (:attr:`~definition.__qualname__`).
    2. Return the functions name (:attr:`~definition.__name__`).
    3. Return the (called) name of the functions type.

    Examples
    --------
    .. code:: python

        >>> from functools import partial
        >>> from nanoutils import get_func_name

        >>> def func1():
        ...     pass

        >>> class Class():
        ...     def func2(self):
        ...         pass

        >>> func3 = partial(len)

        >>> get_func_name(func1)
        'func1'

        >>> get_func_name(func1, prepend_module=True)  # doctest: +SKIP
        '__main__.func1'

        >>> get_func_name(Class.func2)
        'Class.func2'

        >>> get_func_name(func3)
        'partial(...)'

        >>> get_func_name(func3, repr_fallback=True)
        'functools.partial(<built-in function len>)'


    Parameters
    ----------
    func : :class:`~collections.abc.Callable`
        A callable object.
    prepend_module : :class:`bool`
        If :data:`True` prepend the objects module (:attr:`~definition.__module__`),
        if available, to the to-be returned string.
    repr_fallback : :class:`bool`
        By default, when the passed function has neither a :attr:`~definition.__qualname__` or
        :attr:`~definition.__name__` attribute the (called) name of the functions class is returned.
        If :data:`True` then use :func:`repr` instead.

    Returns
    -------
    :class:`str`
        A string representation of the name of **func**.

    """
    try:
        name: str = getattr(func, '__qualname__', func.__name__)
    except AttributeError as ex:
        if not callable(func):
            raise TypeError("'func' expected a callable; "
                            f"observed type: {func.__class__.__name__!r}") from ex
        if repr_fallback:
            name = repr(func)
        else:
            name = f'{func.__class__.__name__}(...)'

    if prepend_module:
        try:
            return f'{func.__module__}.{name}'
        except AttributeError:
            pass
    return name


def group_by_values(iterable: Iterable[Tuple[_VT, _KT]]) -> Dict[_KT, List[_VT]]:
    """Take an iterable, yielding 2-tuples, and group all first elements by the second.

    Examples
    --------
    .. code:: python

        >>> str_list: list = ['a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'c']
        >>> iterator = enumerate(str_list, 1)

        >>> new_dict: dict = group_by_values(iterator)
        >>> print(new_dict)
        {'a': [1, 2, 3, 4, 5], 'b': [6, 7, 8], 'c': [9]}

    Parameters
    ----------
    iterable : :class:`Iterable[Tuple[VT, KT]]<typing.Iterable>`
        An iterable yielding 2 elements upon iteration
        (*e.g.* :meth:`dict.items` or :func:`enumerate`).
        The second element must be :class:`Hashable<collections.abc.Hashable>` and will be used
        as key in the to-be returned mapping.

    Returns
    -------
    :class:`Dict[KT, List[VT]]<typing.Dict>`
        A grouped dictionary.

    """
    ret = {}
    list_append: Dict[_KT, Callable[[_VT], None]] = {}
    for value, key in iterable:
        try:
            list_append[key](value)
        except KeyError:
            ret[key] = [value]
            list_append[key] = ret[key].append
    return ret


def set_docstring(docstring: None | str) -> Callable[[_FT], _FT]:
    """A decorator for assigning docstrings.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import set_docstring

        >>> number = "#10"

        >>> @set_docstring(f"Fancy docstring {number}.")
        ... def func():
        ...     pass

        >>> print(func.__doc__)
        Fancy docstring #10.

    Parameters
    ----------
    docstring : :class:`str`, optional
        The to-be assigned docstring.

    """
    def wrapper(func: _FT) -> _FT:
        func.__doc__ = docstring
        return func
    return wrapper


def get_importable(string: str, validate: None | Callable[[_T], bool] = None) -> _T:
    """Get an importable object.

    Examples
    --------
    .. code:: python

        >>> from inspect import isclass
        >>> from nanoutils import get_importable

        >>> dict_type = get_importable('builtins.dict', validate=isclass)
        >>> print(dict_type)
        <class 'dict'>

    Parameters
    ----------
    string : :class:`str`
        A string representing an importable object.
        Note that the string *must* contain the object's module.
    validate : :data:`~typing.Callable`, optional
        A callable for validating the imported object.
        Will raise a :exc:`RuntimeError` if its output evaluates to ``False``.

    Returns
    -------
    :class:`object`
        The imported object

    """
    try:
        head, *tail = string.split('.')
    except (AttributeError, TypeError) as ex:
        raise TypeError("'string' expected a str; observed type: "
                        f"{string.__class__.__name__!r}") from ex

    ret: _T = importlib.import_module(head)  # type: ignore
    for name in tail:
        ret = getattr(ret, name)

    if validate is None:
        return ret
    elif not validate(ret):
        val_str = get_func_name(validate) + '()'
        raise RuntimeError(f'Passing {ret!r} to {val_str} failed to return True')
    return ret


@overload
def split_dict(
    dct: MutableMapping[_KT, _VT],
    preserve_order: bool = ...,
    *,
    keep_keys: Iterable[_KT],
) -> Dict[_KT, _VT]:
    ...
@overload  # noqa: E302
def split_dict(
    dct: MutableMapping[_KT, _VT],
    preserve_order: bool = ...,
    *,
    disgard_keys: Iterable[_KT],
) -> Dict[_KT, _VT]:
    ...
def split_dict(dct, preserve_order=False, *, keep_keys=None, disgard_keys=None):  # noqa: E302,E501
    r"""Pop all items from **dct** which are in not in **keep_keys** and use them to construct a new dictionary.

    Note that, by popping its keys, the passed **dct** will also be modified inplace.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import split_dict

        >>> dict1 = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
        >>> dict2 = split_dict(dict1, keep_keys={1, 2})

        >>> print(dict1, dict2, sep='\n')
        {1: 'a', 2: 'b'}
        {3: 'c', 4: 'd'}

        >>> dict3 = split_dict(dict1, disgard_keys={1, 2})
        >>> print(dict1, dict3, sep='\n')
        {}
        {1: 'a', 2: 'b'}

    Parameters
    ----------
    dct : :class:`MutableMapping[KT, VT]<typing.MutableMapping>`
        A mutable mapping.
    preserve_order : :class:`bool`
        If :data:`True`, preserve the order of the items in **dct**.
        Note that :code:`preserve_order = False` is generally faster.
    keep_keys : :class:`Iterable[KT]<typing.Iterable>`, keyword-only
        An iterable with keys that should remain in **dct**.
        Note that **keep_keys** and **disgard_keys** are mutually exclusive.
    disgard_keys : :class:`Iterable[KT]<typing.Iterable>`, keyword-only
        An iterable with keys that should be removed from **dct**.
        Note that **disgard_keys** and **keep_keys** are mutually exclusive.

    Returns
    -------
    :class:`Dict[KT, VT]<typing.Dict>`
        A new dictionaries with all key/value pairs from **dct** not specified in **keep_keys**.

    """  # noqa: E501
    if keep_keys is disgard_keys is None:
        raise TypeError("'keep_keys' and 'disgard_keys' cannot both be unspecified")
    elif keep_keys is None:
        iterable = _disgard_keys(dct, disgard_keys, preserve_order)
    elif disgard_keys is None:
        iterable = _keep_keys(dct, keep_keys, preserve_order)
    else:
        raise TypeError("'keep_keys' and 'disgard_keys' cannot both be specified")

    return {k: dct.pop(k) for k in iterable}


def _keep_keys(
    dct: Mapping[_KT, _VT],
    keep_keys: Iterable[_KT],
    preserve_order: bool = False,
) -> Collection[_KT]:
    """A helper function for :func:`split_dict`; used when :code:`keep_keys is not None`."""
    if preserve_order:
        return [k for k in dct if k not in keep_keys]
    else:
        try:
            return dct.keys() - keep_keys  # type: ignore
        except TypeError:
            return set(dct.keys()).difference(keep_keys)


def _disgard_keys(
    dct: Mapping[_KT, _VT],
    keep_keys: Iterable[_KT],
    preserve_order: bool = False,
) -> Collection[_KT]:
    """A helper function for :func:`split_dict`; used when :code:`disgard_keys is not None`."""
    if preserve_order:
        return [k for k in dct if k in keep_keys]
    else:
        try:
            return dct.keys() & keep_keys  # type: ignore
        except TypeError:
            return set(dct.keys()).intersection(keep_keys)


@overload
def raise_if(exception: None) -> Callable[[_FT], _FT]:
    ...
@overload  # noqa: E302
def raise_if(exception: BaseException) -> Callable[[Callable[..., Any]], Callable[..., NoReturn]]:
    ...
def raise_if(exception):  # noqa: E302
    """A decorator which raises the passed exception whenever calling the decorated function.

    If **exception** is :data:`None` then the decorated function will be called as usual.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import raise_if

        >>> ex1 = None
        >>> ex2 = TypeError("This is an exception")

        >>> @raise_if(ex1)
        ... def func1() -> bool:
        ...     return True

        >>> @raise_if(ex2)
        ... def func2() -> bool:
        ...     return True

        >>> func1()
        True

        >>> func2()
        Traceback (most recent call last):
          ...
        TypeError: This is an exception


    Parameters
    ----------
    exception : :exc:`BaseException`, optional
        An exception.
        If :data:`None` is passed then the decorated function will be called as usual.

    See Also
    --------
    :func:`nanoutils.ignore_if`
        A decorator which, if an exception is passed, ignores calls to the decorated function.

    """
    if exception is None:
        def decorator1(func: _FT) -> _FT:
            return func
        return decorator1

    elif isinstance(exception, BaseException):
        def decorator2(func: Callable[..., Any]) -> Callable[..., NoReturn]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> NoReturn:
                raise exception
            return wrapper
        return decorator2

    else:
        raise TypeError(f"{exception.__class__.__name__!r}")


@overload
def ignore_if(exception: None, warn: bool = ...) -> Callable[[_FT], _FT]:
    ...
@overload  # noqa: E302
def ignore_if(exception: BaseException, warn: bool = ...) -> Callable[[Callable[..., Any]], Callable[..., None]]:  # noqa: E501
    ...
def ignore_if(exception, warn=True):  # noqa: E302
    """A decorator which, if an exception is passed, ignores calls to the decorated function.

    If **exception** is :data:`None` then the decorated function will be called as usual.

    Examples
    --------
    .. code:: python

        >>> import warnings
        >>> from nanoutils import ignore_if

        >>> ex1 = None
        >>> ex2 = TypeError("This is an exception")

        >>> @ignore_if(ex1)
        ... def func1() -> bool:
        ...     return True

        >>> @ignore_if(ex2)
        ... def func2() -> bool:
        ...     return True

        >>> func1()
        True

        >>> func2()

        # Catch the warning and a raise it as an exception
        >>> with warnings.catch_warnings():
        ...     warnings.simplefilter("error", UserWarning)
        ...     func2()
        Traceback (most recent call last):
          ...
        UserWarning: Skipping call to func2()

    Parameters
    ----------
    exception : :exc:`BaseException`, optional
        An exception.
        If :data:`None` is passed then the decorated function will be called as usual.
    warn : :class:`bool`
        If :data:`True` issue a :exc:`UserWarning` whenever calling the decorated function

    See Also
    --------
    :func:`nanoutils.raise_if`
        A decorator which raises the passed exception whenever calling the decorated function.

    """
    _WARN = warn

    if exception is None:
        def decorator1(func: _FT) -> _FT:
            return func
        return decorator1

    elif isinstance(exception, BaseException):
        def decorator2(func: Callable[..., Any]) -> Callable[..., None]:
            msg = f"Skipping call to {get_func_name(func)}()"

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> None:
                if _WARN:
                    exc = UserWarning(msg)
                    exc.__cause__ = exception
                    warnings.warn(exc)
                    return None
            return wrapper
        return decorator2

    else:
        raise TypeError(f"{exception.__class__.__name__!r}")


_PATTERN = re.compile("([0-9]+).([0-9]+).([0-9]+)")


class VersionInfo(NamedTuple):
    """A :func:`~collections.namedtuple` representing the version of a package.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import VersionInfo

        >>> version = '0.8.2'
        >>> VersionInfo.from_str(version)
        VersionInfo(major=0, minor=8, micro=2)

    """

    #: :class:`int`: The semantic_ major version.
    major: int

    #: :class:`int`: The semantic_ minor version.
    minor: int

    #: :class:`int`: The semantic_ micro version (a.k.a. :attr:`VersionInfo.patch`).
    micro: int

    @property
    def patch(self) -> int:
        """:class:`int`: An alias for :attr:`VersionInfo.micro`."""
        return self.micro

    @classmethod
    def from_str(
        cls,
        version: str,
        *,
        fullmatch: bool = True,
    ) -> VersionInfo:
        """Construct a :class:`VersionInfo` from a string.

        Parameters
        ----------
        version : :class:`str`
            A string representation of a version (*e.g.* :code:`version = "0.8.2"`).
            The string should contain three ``"."`` separated integers, respectively,
            representing the major, minor and micro/patch versions.
        fullmatch : :class:`bool`
            Whether the version-string must consist exclusivelly of three
            period-separated integers, or if a substring is also allowed.

        Returns
        -------
        :class:`nanoutils.VersionInfo`
            A new VersionInfo instance.

        """
        match = _PATTERN.fullmatch(version) if fullmatch else _PATTERN.match(version)
        if match is None:
            raise ValueError(f"Failed to parse {version!r}")
        return cls._make(int(i) for i in match.groups())


def _get_directive(
    obj: object,
    name: str,
    decorators: Container[str] = EMPTY_CONTAINER,
) -> str:
    """A helper function for :func:`~nanoutils.construct_api_doc`."""
    if isinstance(obj, type):
        if issubclass(obj, BaseException):
            return f'.. autoexception:: {name}'
        return f'.. autoclass:: {name}\n    :members:'

    elif callable(obj):
        if name in decorators:
            return f'.. autodecorator:: {name}'
        return f'.. autofunction:: {name}'

    elif isinstance(obj, ModuleType):
        return f'.. automodule:: {name}'

    else:
        return f'.. autodata:: {name}'


def construct_api_doc(
    glob_dict: Mapping[str, object],
    decorators: Container[str] = EMPTY_CONTAINER,
) -> str:
    '''Format a **Nano-Utils** module-level docstring.

    Examples
    --------
    .. code:: python

        >>> __doc__ = """
        ... Index
        ... -----
        ... .. autosummary::
        ... {autosummary}
        ...
        ... API
        ... ---
        ... {autofunction}
        ...
        ... """

        >>> from nanoutils import construct_api_doc

        >>> __all__ = ['obj', 'func', 'Class']

        >>> obj = ...

        >>> def func(obj: object) -> None:
        ...     pass

        >>> class Class(object):
        ...     pass

        >>> doc = construct_api_doc(locals())
        >>> print(doc)
        <BLANKLINE>
        Index
        -----
        .. autosummary::
            obj
            func
            Class
        <BLANKLINE>
        API
        ---
        .. autodata:: obj
        .. autofunction:: func
        .. autoclass:: Class
            :members:
        <BLANKLINE>
        <BLANKLINE>

    Parameters
    ----------
    glob_dict : :class:`Mapping[str, object]<typing.Mapping>`
        A mapping containg a module-level namespace.
        Note that the mapping *must* contain the ``"__doc__"`` and ``"__all__"`` keys.

    decorators : :class:`Container[str]<typing.Container>`
        A container with the names of all decorators.
        If not specified, all functions will use the Sphinx ``autofunction`` domain.

    Returns
    -------
    :class:`str`
        The formatted string.

    '''
    __doc__ = cast(str, glob_dict['__doc__'])
    __all__ = cast(List[str], glob_dict['__all__'])

    return __doc__.format(
        autosummary='\n'.join(f'    {i}' for i in __all__),
        autofunction='\n'.join(_get_directive(glob_dict[i], i, decorators) for i in __all__)
    )


def _null_func(obj: _T) -> _T:
    """Return the passed object."""
    return obj


__doc__ = construct_api_doc(globals(), decorators={'set_docstring', 'raise_if', 'ignore_if'})
