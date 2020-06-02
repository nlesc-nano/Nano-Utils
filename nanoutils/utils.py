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

import os
import importlib
from types import MappingProxyType, ModuleType
from functools import partial
from typing import (
    List,
    Tuple,
    Optional,
    Callable,
    TypeVar,
    Mapping,
    Union,
    Any,
    Iterable,
    Dict,
    Collection,
    Container
)

from .empty import EMPTY_COLLECTION

__all__ = ['PartialPrepend',
           'group_by_values', 'get_importable', 'set_docstring', 'load_readme',
           'construct_api_doc']

T = TypeVar('T')
KT = TypeVar('KT')
VT = TypeVar('VT')
FT = TypeVar('FT', bound=Callable)


def group_by_values(iterable: Iterable[Tuple[VT, KT]]) -> Dict[KT, List[VT]]:
    """Take an iterable, yielding 2-tuples, and group all first elements by the second.

    Exameple
    --------
    .. code:: python

        >>> str_list: list = ['a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'c']
        >>> iterator = enumerate(str_list)

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


#: A mapping with the default value for the **replace** argument of :func:`load_readme`.
README_MAPPING: Mapping[str, str] = MappingProxyType({
    '``': '|',
    '()': ''
})


def load_readme(readme: Union[str, bytes, int, os.PathLike],
                replace: Mapping[str, str] = README_MAPPING,
                **kwargs: Any) -> str:
    r"""Load and return the content of a readme file located in the same directory as this file.

    Parameters
    ----------
    readme : :class:`int` or `path-like <https://docs.python.org/3/glossary.html#term-path-like-object>`_
        The name of the readme file.
    replace : :class:`Mapping[str, str]<typing.Mapping>`
        A mapping of to-be replaced substrings contained within the readme file.
    \**kwargs : :data:`~typing.Any`
        Optional keyword arguments for :func:`open`.

    Returns
    -------
    :class:`str`
        The content of **readme** as string.

    """  # noqa: E501
    with open(readme, **kwargs) as f:
        ret: str = f.read()
    for old, new in replace.items():
        ret = ret.replace(old, new)
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
        "Fancy docstrings #10."

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

        >>> from nanoutils import get_importable

        >>> def is_class(obj: object) -> bool:
        ...     return isinstance(obj, type)

        >>> dict_type = get_importable('builtins.dict', validate=is_class)
        >>> print(dict_type)
        <class 'dict'>

    Parameters
    ----------
    string : :class:`str`
        A string representing an importable object.
        Note that the string *must* contain the object's module.
    validate : :class:`~typing.Callable`, optional
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
        raise RuntimeError(f'Passing {ret!r} to {validate!r} failed to return True')
    return ret


class PartialPrepend(partial):
    """A :class:`~functools.partial` subclass where the ``*args`` are appended rather than prepended."""  # noqa: E501

    def __call__(self, *args, **keywords):
        """Call and return :attr:`~PartialReversed.func`."""
        keywords = {**self.keywords, **keywords}
        return self.func(*args, *self.args, **keywords)


def _get_directive(obj: object, name: str,
                   decorators: Container[str] = EMPTY_COLLECTION) -> str:
    if isinstance(obj, type):
        if issubclass(obj, BaseException):
            return f'.. autoexception:: {name}'
        return f'.. autoclass:: {name}'

    elif callable(obj):
        if name in decorators:
            return f'.. autodecorator:: {name}'
        return f'.. autofunction:: {name}'

    elif isinstance(obj, ModuleType):
        return f'.. automodule:: {name}'

    else:
        return f'.. autodata:: {name}'


def construct_api_doc(glob_dict: Dict[str, Any],
                      decorators: Container[str] = EMPTY_COLLECTION) -> str:
    __doc__ = glob_dict['__doc__']
    __all__ = glob_dict['__all__']

    return __doc__.format(
        autosummary='\n'.join(f'    {i}' for i in __all__),
        autofunction='\n'.join(_get_directive(glob_dict[i], i) for i in __all__)
    )

__doc__ = construct_api_doc(globals(), decorators={'set_docstring'})
