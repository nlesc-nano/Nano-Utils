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

# flake8: noqa: E402

from __future__ import annotations

import re
import warnings
import importlib
import inspect
import functools
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
    MutableMapping,
    Collection,
    cast,
    overload,
)

from .typing_utils import Literal
from .empty import EMPTY_CONTAINER

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
    'positional_only',
    'UserMapping',
    'MutableUserMapping',
    'warning_filter',
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
            return dct.keys() - keep_keys
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
            return dct.keys() & keep_keys
        except TypeError:
            return set(dct.keys()).intersection(keep_keys)


def raise_if(exception: None | BaseException) -> Callable[[_FT], _FT]:
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
        def decorator2(func: _FT) -> _FT:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                raise exception  # type: ignore[misc]
            return wrapper  # type: ignore[return-value]
        return decorator2

    else:
        raise TypeError(f"{exception.__class__.__name__!r}")


def ignore_if(exception: None | BaseException, warn: bool = True) -> Callable[[_FT], _FT]:
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
        def decorator2(func: _FT) -> _FT:
            msg = f"Skipping call to {get_func_name(func)}()"

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> None:
                if _WARN:
                    exc = UserWarning(msg)
                    exc.__cause__ = exception
                    warnings.warn(exc)
                    return None
            return wrapper  # type: ignore[return-value]
        return decorator2

    else:
        raise TypeError(f"{exception.__class__.__name__!r}")


# See PEP 440 Apendix B
_PATTERN_STR = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""
_PATTERN = re.compile(
    r"^\s*" + _PATTERN_STR + r"\s*$",
    re.VERBOSE | re.IGNORECASE,
)


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
    minor: int = 0

    #: :class:`int`: The semantic_ micro version.
    micro: int = 0

    @property
    def patch(self) -> int:
        """:class:`int`: An alias for :attr:`VersionInfo.micro`."""
        return self.micro

    @property
    def maintenance(self) -> int:
        """:class:`int`: An alias for :attr:`VersionInfo.micro`."""
        return self.micro

    @property
    def bug(self) -> int:
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
            A PEP 440-compatible version string(*e.g.* :code:`version = "0.8.2"`).
            Note that version representations are truncated at up to three integers.
        fullmatch : :class:`bool`
            Whether to perform a full or partial match on the passed string.

        Returns
        -------
        :class:`nanoutils.VersionInfo`
            A new VersionInfo instance.

        See Also
        --------
        :pep:`440`
            This PEP describes a scheme for identifying versions of Python software distributions,
            and declaring dependencies on particular versions.

        """
        match = _PATTERN.fullmatch(version) if fullmatch else _PATTERN.match(version)
        if match is None:
            raise ValueError(f"Failed to parse {version!r}")
        return cls._make(int(i) for i in match["release"].split(".")[:3])


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


def positional_only(func: _FT) -> _FT:
    """A decorator for converting mangled parameters to positional-only.

    Sets the ``__signature__`` attribute of the decorated function.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import positional_only
        >>> import inspect

        >>> def func1(__a, b=None):
        ...     pass

        >>> print(inspect.signature(func1))
        (__a, b=None)

        >>> @positional_only
        ... def func2(__a, b=None):
        ...     pass

        >>> print(inspect.signature(func2))
        (a, /, b=None)

    Parameters
    ----------
    func : :class:`~collections.abc.Callable`
        The to-be decorated function whose ``__signature__`` attribute will be added or updated.

    """
    # Check if any name mangling has occured
    cls_name, period, _ = getattr(func, "__qualname__", "").partition(".")
    prefix = "__" if not period else f"_{cls_name}__"
    offset = len(prefix)

    # Identify the if `__`-prefixed parameters
    sgn = inspect.signature(func)
    pos_only_list = []
    for j, name in enumerate(sgn.parameters):
        if name.startswith(prefix):
            pos_only_list.append(j)

    if not pos_only_list:
        func.__signature__ = sgn  # type: ignore[attr-defined]
        return func
    else:
        j = pos_only_list[-1]

    # Unmangle parameters and convert them to positional-only
    prm_list = []
    for i, (name, prm) in enumerate(sgn.parameters.items()):
        if i <= j:
            if name.startswith(prefix):
                name = name[offset:]
            prm = prm.replace(name=name, kind=inspect.Parameter.POSITIONAL_ONLY)
        prm_list.append(prm)

    func.__signature__ = inspect.Signature(   # type: ignore[attr-defined]
        parameters=prm_list,
        return_annotation=sgn.return_annotation,
    )
    func.__annotations__ = {
        (k[offset:] if k.startswith(prefix) else k): v for k, v in func.__annotations__.items()
    }
    return func


def warning_filter(
    action: Literal["default", "error", "ignore", "always", "module", "once"],
    message: str = "",
    category: type[Warning] = Warning,
    module: str = "",
    lineno: int = 0,
    append: bool = False,
) -> Callable[[_FT], _FT]:
    """A decorator for wrapping function calls with :func:`warnings.filterwarnings`.

    Examples
    --------
    .. code-block:: python

        >>> from nanoutils import warning_filter
        >>> import warnings

        >>> @warning_filter("error", category=UserWarning)
        ... def func():
        ...     warnings.warn("test", UserWarning)

        >>> func()
        Traceback (most recent call last):
            ...
        UserWarning: test

    Parameters
    ----------
    action : :class:`str`
        One of the following strings:

        * ``"default"``: Print the first occurrence of matching warnings for each location (module + line number) where the warning is issued
        * ``"error"``: Turn matching warnings into exceptions
        * ``"ignore"``: Never print matching warnings
        * ``"always"``: Always print matching warnings
        * ``"module"``: Print the first occurrence of matching warnings for each module where the warning is issued (regardless of line number)
        * ``"once"``: Print only the first occurrence of matching warnings, regardless of location

    message : :class:`str`, optional
        A string containing a regular expression that the start of the warning message must match.
        The expression is compiled to always be case-insensitive.
    category : :class:`type[Warning] <type>`
        The to-be affected :class:`Warning` (sub-)class.
    module : :class:`str`, optional
        A string containing a regular expression that the module name must match.
        The expression is compiled to be case-sensitive.
    lineno : :class:`int`
        An integer that the line number where the warning occurred must match,
        or 0 to match all line numbers.
    append : :class:`bool`
        Whether the warning entry is inserted at the end.

    See Also
    --------
    :func:`warnings.filterwarnings` :
        Insert a simple entry into the list of warnings filters (at the front).

    """  # noqa: E501
    def decorator(func: _FT) -> _FT:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with warnings.catch_warnings():
                warnings.filterwarnings(action, message, category, module, lineno, append)
                ret = func(*args, **kwargs)
            return ret
        return cast(_FT, wrapper)
    return decorator


# Move to the end to reduce the risk of circular imports
from ._partial import PartialPrepend
from ._set_attr import SetAttr
from ._seq_view import SequenceView
from ._catch_err import CatchErrors
from ._lazy_import import LazyImporter, MutableLazyImporter
from ._user_dict import UserMapping, MutableUserMapping

__doc__ = construct_api_doc(
    globals(),
    decorators={'set_docstring', 'raise_if', 'ignore_if', 'positional_only', 'warning_filter'},
)
