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
from functools import partial
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
    cast
)

from .empty import EMPTY_CONTAINER

__all__ = [
    'PartialPrepend', 'VersionInfo',
    'group_by_values', 'get_importable', 'set_docstring', 'construct_api_doc'
]

T = TypeVar('T')
KT = TypeVar('KT')
VT = TypeVar('VT')
FT = TypeVar('FT', bound=Callable)


def group_by_values(iterable: Iterable[Tuple[VT, KT]]) -> Dict[KT, List[VT]]:
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
    list_append: Dict[KT, Callable[[VT], None]] = {}
    for value, key in iterable:
        try:
            list_append[key](value)
        except KeyError:
            ret[key] = [value]
            list_append[key] = ret[key].append
    return ret


def set_docstring(docstring: Optional[str]) -> Callable[[FT], FT]:
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
    def wrapper(func: FT) -> FT:
        func.__doc__ = docstring
        return func
    return wrapper


def get_importable(string: str, validate: Optional[Callable[[T], bool]] = None) -> T:
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

    ret: T = importlib.import_module(head)  # type: ignore
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

    #: int: The semantic_ major version.
    major: int

    #: int: The semantic_ minor version.
    minor: int

    #: int: The semantic_ micro version (a.k.a. :attr:`~VersionInfo.patch`).
    micro: int

    @property
    def patch(self) -> int:
        """An alias for :attr:`~VersionInfo.micro`."""
        return self.micro

    @classmethod
    def from_str(cls, version: str) -> 'VersionInfo':
        """Construct a :class:`VersionInfo` from a string; *e.g.*: :code:`version = "0.8.2"`."""
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


__doc__ = construct_api_doc(globals(), decorators={'set_docstring'})
