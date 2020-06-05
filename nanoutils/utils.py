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

import importlib
from types import ModuleType
from functools import partial, wraps
from typing import (
    List,
    Tuple,
    Optional,
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
    overload,
    TYPE_CHECKING
)

from .empty import EMPTY_CONTAINER

if TYPE_CHECKING:
    from .utils import VersionInfo as VersionInfoType
else:
    VersionInfoType = 'nanoutils.VersionInfo'

__all__ = [
    'PartialPrepend', 'VersionInfo',
    'group_by_values', 'get_importable', 'set_docstring', 'construct_api_doc', 'raise_if',
    'split_dict'
]

_T = TypeVar('_T')
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')
_FT = TypeVar('_FT', bound=Callable)


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


def set_docstring(docstring: Optional[str]) -> Callable[[_FT], _FT]:
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


def get_importable(string: str, validate: Optional[Callable[[_T], bool]] = None) -> _T:
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
        try:
            val_str = f'{validate.__qualname__}()'
        except AttributeError:
            val_str = f'{validate.__class__.__name__}(...)()'

        raise RuntimeError(f'Passing {ret!r} to {val_str} failed to return True')
    return ret


class PartialPrepend(partial):
    """A :func:`~functools.partial` subclass where the ``*args`` are appended rather than prepended.

    Examples
    --------
    .. code:: python

        >>> from functools import partial
        >>> from nanoutils import PartialPrepend

        >>> func1 = partial(isinstance, 1)  # isinstance(1, ...)
        >>> func2 = PartialPrepend(isinstance, float)  # isinstance(..., float)

        >>> func1(int)  # isinstance(1, int)
        True

        >>> func2(1.0)  # isinstance(1.0, float)
        True

    """  # noqa: E501

    def __call__(self, *args, **keywords):
        """Call and return :attr:`~PartialReversed.func`."""
        keywords = {**self.keywords, **keywords}
        return self.func(*args, *self.args, **keywords)


@overload
def split_dict(dct: MutableMapping[_KT, _VT], preserve_order: bool = ..., *,
               keep_keys: Iterable[_KT]) -> Dict[_KT, _VT]:
    ...
@overload  # noqa: E302
def split_dict(dct: MutableMapping[_KT, _VT], preserve_order: bool = ..., *,
               disgard_keys: Iterable[_KT]) -> Dict[_KT, _VT]:
    ...
def split_dict(dct: MutableMapping[_KT, _VT], preserve_order: bool = False, *, keep_keys: Iterable[_KT] = None, disgard_keys: Iterable[_KT] = None) -> Dict[_KT, _VT]:  # noqa: E302,E501
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
    elif keep_keys is not None:
        iterable = _keep_keys(dct, keep_keys, preserve_order)
    elif disgard_keys is not None:
        iterable = _disgard_keys(dct, disgard_keys, preserve_order)
    else:
        raise TypeError("'keep_keys' and 'disgard_keys' cannot both be specified")

    return {k: dct.pop(k) for k in iterable}


def _keep_keys(dct: Mapping[_KT, _VT], keep_keys: Iterable[_KT],
               preserve_order: bool = False) -> Collection[_KT]:
    """A helper function for :func:`split_dict`; used when :code:`keep_keys is not None`."""
    if preserve_order:
        return [k for k in dct if k not in keep_keys]
    else:
        try:
            return dct.keys() - keep_keys  # type: ignore
        except TypeError:
            return set(dct.keys()).difference(keep_keys)


def _disgard_keys(dct: Mapping[_KT, _VT], keep_keys: Iterable[_KT],
                  preserve_order: bool = False) -> Collection[_KT]:
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
def raise_if(exception: BaseException) -> Callable[[Callable], Callable[..., NoReturn]]:
    ...
def raise_if(exception: Optional[BaseException]) -> Callable:  # noqa: E302
    """A decorator which raises the passed exception whenever calling the decorated function.

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

    """
    if exception is None:
        def decorator(func: _FT):
            return func

    elif isinstance(exception, BaseException):
        def decorator(func: _FT):
            @wraps(func)
            def wrapper(*args, **kwargs):
                raise exception
            return wrapper

    else:
        raise TypeError(f"{exception.__class__.__name__!r}")
    return decorator


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
        """An alias for :attr:`VersionInfo.micro`."""
        return self.micro

    @classmethod
    def from_str(cls, version: str) -> VersionInfoType:
        """Construct a :class:`VersionInfo` from a string; *e.g.* :code:`version = "0.8.2"`."""
        if not isinstance(version, str):
            cls_name = version.__class__.__name__
            raise TypeError(f"'version' expected a string; observed type: {cls_name!r}")

        try:
            major, minor, micro = (int(i) for i in version.split('.'))
        except (ValueError, TypeError) as ex:
            raise ValueError("'version' expected a string consisting of three '.'-separated "
                             f"integers (e.g. '0.8.2'); observed value: {version!r}") from ex
        return cls(major=major, minor=minor, micro=micro)


def _get_directive(obj: object, name: str,
                   decorators: Container[str] = EMPTY_CONTAINER) -> str:
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


def construct_api_doc(glob_dict: Mapping[str, object],
                      decorators: Container[str] = EMPTY_CONTAINER) -> str:
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
        autofunction='\n'.join(_get_directive(glob_dict[i], i) for i in __all__)
    )


def _null_func(obj: _T) -> _T:
    """Return the passed object."""
    return obj


__doc__ = construct_api_doc(globals(), decorators={'set_docstring', 'raise_if'})
