"""Utility functions related to :mod:`numpy`.

Note that these functions require the NumPy package.

See Also
--------
.. image:: https://badge.fury.io/py/numpy.svg
    :target: https://badge.fury.io/py/numpy

**NumPy** is the fundamental package needed for scientific computing with Python.
It provides:

* a powerful N-dimensional array object
* sophisticated (broadcasting) functions
* tools for integrating C/C++ and Fortran code
* useful linear algebra, Fourier transform, and random number capabilities


Index
-----
.. currentmodule:: nanoutils
.. autosummary::
{autosummary}

API
---
{autofunction}

"""

from math import nan
from typing import TYPE_CHECKING, Optional, Union, Iterable, TypeVar, Callable, overload
from itertools import combinations, permutations, combinations_with_replacement, chain
from collections import abc

from .utils import raise_if, construct_api_doc
from .typing_utils import ArrayLike, DtypeLike

try:
    import numpy as np
    NUMPY_EX: Optional[Exception] = None
except Exception as ex:
    NUMPY_EX = ex

if TYPE_CHECKING:
    from numpy import ndarray
else:
    ndarray = 'numpy.ndarray'

__all__ = ['as_nd_array', 'array_combinations', 'array_combinations_with_replacement',
           'array_permutations', 'fill_diagonal_blocks']

_T = TypeVar('_T')
_NDT = TypeVar('_NDT', bound=ndarray)

_CombFunc = Callable[[Iterable[_T], int], Iterable[Iterable[_T]]]


@raise_if(NUMPY_EX)
def as_nd_array(array: Union[Iterable, ArrayLike], dtype: DtypeLike,
                ndmin: int = 1, copy: bool = False) -> ndarray:
    """Construct a numpy array from an iterable or array-like object.

    Examples
    --------
    .. doctest:: python
        :skipif: NUMPY_EX is not None

        >>> from nanoutils import as_nd_array

        >>> as_nd_array(1, int)
        array([1])

        >>> as_nd_array([1, 2, 3, 4], int)
        array([1, 2, 3, 4])

        >>> iterator = iter([1, 2, 3, 4])
        >>> as_nd_array(iterator, int)
        array([1, 2, 3, 4])


    Parameters
    ----------
    array : :class:`~collections.abc.Iterable` or array-like
        An array-like object or an iterable consisting of scalars.
    dtype : :class:`type` or :class:`numpy.dtype`
        The data type of the to-be returned array.
    ndmin : :class:`int`
        The minimum dimensionality of the to-be returned array.
    copy : :class:`bool`
        If :data:`True`, always return a copy.

    Returns
    -------
    :class:`numpy.ndarray`
        A numpy array constructed from **value**.

    """
    try:
        return np.array(array, dtype=dtype, ndmin=ndmin, copy=copy)

    except TypeError as ex:
        if not isinstance(array, abc.Iterable):
            raise ex

        ret: ndarray = np.fromiter(array, dtype=dtype)
        ret.shape += (ndmin - ret.ndim) * (1,)
        return ret


_ERR = '{} requires an array of at least one dimension'


@overload
def array_combinations(a: ArrayLike, r: int, axis: int = ..., out: _NDT = ...) -> _NDT:
    ...
@overload  # noqa: E302
def array_combinations(a: _NDT, r: int, axis: int = ..., out: None = ...) -> _NDT:
    ...
@overload  # noqa: E302
def array_combinations(a: ArrayLike, r: int, axis: int = ..., out: None = ...) -> ndarray:
    ...
@raise_if(NUMPY_EX)  # noqa: E302
def array_combinations(array, r, axis=-1, out=None):
    r"""Create a new array by creating all **array** combinations of length **r** along a user-specified **axis**.

    Examples
    --------
    .. doctest:: python
        :skipif: NUMPY_EX is not None

        >>> from nanoutils import array_combinations

        >>> array = [[1, 2, 3],
        ...          [4, 5, 6]]

        >>> array_combinations(array, r=2)
        array([[[1, 2],
                [1, 3],
                [2, 3]],
        <BLANKLINE>
               [[4, 5],
                [4, 6],
                [5, 6]]])

    Parameters
    ----------
    array : array-like, ndim :math:`n`
        The input array of at least one dimension.
    r : :class:`int`
        The length of each combination.
    axis : :class:`int`
        The axis used for constructing the combinations.
    out : :class:`numpy.ndarray`, optional
        Alternative output array in which to place the result.
        It must have the same shape as the expected output,
        but the type of the output values will be cast if necessary.

    Returns
    -------
    :class:`numpy.ndarray`, ndim :math:`n + 1`
        A new array with all **ar** combinations (of length **r**)
        along the user-specified **axis**.

    See Also
    --------
    :func:`itertools.combinations`
        Return successive r-length combinations of elements in the iterable.

    """  # noqa: E501
    a = np.asanyarray(array)
    if not a.ndim:
        raise ValueError(_ERR.format('array_combinations'))

    return _combinator(a, r, combinations, axis, out)


@overload
def array_combinations_with_replacement(a: ArrayLike, r: int, axis: int = ..., out: _NDT = ...) -> _NDT:  # noqa: E501
    ...
@overload  # noqa: E302
def array_combinations_with_replacement(a: _NDT, r: int, axis: int = ..., out: None = ...) -> _NDT:
    ...
@overload  # noqa: E302
def array_combinations_with_replacement(a: ArrayLike, r: int, axis: int = ..., out: None = ...) -> ndarray:  # noqa: E501
    ...
@raise_if(NUMPY_EX)  # noqa: E302
def array_combinations_with_replacement(array, r, axis=-1, out=None):
    r"""Create a new array by creating all **array** combinations with replacements of length **r** along a user-specified **axis**.

    Examples
    --------
    .. doctest:: python
        :skipif: NUMPY_EX is not None

        >>> from nanoutils import array_combinations_with_replacement

        >>> array = [[1, 2, 3],
        ...          [4, 5, 6]]

        >>> array_combinations_with_replacement(array, r=2)
        array([[[1, 1],
                [1, 2],
                [1, 3],
                [2, 2],
                [2, 3],
                [3, 3]],
        <BLANKLINE>
               [[4, 4],
                [4, 5],
                [4, 6],
                [5, 5],
                [5, 6],
                [6, 6]]])

    Parameters
    ----------
    array : array-like, ndim :math:`n`
        The input array of at least one dimension.
    r : :class:`int`
        The length of each combination.
    axis : :class:`int`
        The axis used for constructing the combinations.
    out : :class:`numpy.ndarray`, optional
        Alternative output array in which to place the result.
        It must have the same shape as the expected output,
        but the type of the output values will be cast if necessary.

    Returns
    -------
    :class:`numpy.ndarray`, ndim :math:`n + 1`
        A new array with all **ar** combinations with replacement (of length **r**)
        along the user-specified **axis**.

    See Also
    --------
    :func:`itertools.combinations_with_replacement`
        Return successive r-length combinations of elements in the iterable
        allowing individual elements to have successive repeats.

    """  # noqa: E501
    a = np.asanyarray(array)
    if not a.ndim:
        raise ValueError(_ERR.format('array_combinations_with_replacement'))

    return _combinator(a, r, combinations_with_replacement, axis, out)


@overload
def array_permutations(a: ArrayLike, r: int, axis: int = ..., out: _NDT = ...) -> _NDT:
    ...
@overload  # noqa: E302
def array_permutations(a: _NDT, r: int, axis: int = ..., out: None = ...) -> _NDT:
    ...
@overload  # noqa: E302
def array_permutations(a: ArrayLike, r: int, axis: int = ..., out: None = ...) -> ndarray:
    ...
@raise_if(NUMPY_EX)  # noqa: E302
def array_permutations(array, r, axis=-1, out=None):
    r"""Create a new array by creating all **array** permutations of length **r** along a user-specified **axis**.

    Examples
    --------
    .. doctest:: python
        :skipif: NUMPY_EX is not None

        >>> from nanoutils import array_permutations

        >>> array = [[1, 2, 3],
        ...          [4, 5, 6]]

        >>> array_permutations(array, r=2)
        array([[[1, 2],
                [1, 3],
                [2, 1],
                [2, 3],
                [3, 1],
                [3, 2]],
        <BLANKLINE>
               [[4, 5],
                [4, 6],
                [5, 4],
                [5, 6],
                [6, 4],
                [6, 5]]])

    Parameters
    ----------
    array : array-like, ndim :math:`n`
        The input array of at least one dimension.
    r : :class:`int`
        The length of each permutation.
    axis : :class:`int`
        The axis used for constructing the permutations.
    out : :class:`numpy.ndarray`, optional
        Alternative output array in which to place the result.
        It must have the same shape as the expected output,
        but the type of the output values will be cast if necessary.

    Returns
    -------
    :class:`numpy.ndarray`, ndim :math:`n + 1`
        A new array with all **ar** permutations (of length **r**)
        along the user-specified **axis**.

    See Also
    --------
    :func:`itertools.permutations`
        Return successive r-length permutations of elements in the iterable.

    """  # noqa: E501
    a = np.asanyarray(array)
    if not a.ndim:
        raise ValueError(_ERR.format('array_permutations'))

    return _combinator(a, r, permutations, axis, out)


@overload
def _combinator(a: _NDT, r: int, func: _CombFunc, axis: int = ..., out: None = ...) -> _NDT:
    ...
@overload  # noqa: E302
def _combinator(a: ndarray, r: int, func: _CombFunc, axis: int = ..., out: _NDT = ...) -> _NDT:
    ...
@raise_if(NUMPY_EX)  # noqa: E302
def _combinator(a, r, func, axis=-1, out=None):
    """Helper function for doing combinatorics."""
    try:
        n = a.shape[axis]
        n_range = range(n)  # raises a TypeError if `axis` is a slice
    except IndexError:
        raise np.AxisError(axis, ndim=a.ndim) from None
    except TypeError:
        cls_name = axis.__class__.__name__
        raise TypeError(f'{cls_name!r} object cannot be interpreted as an integer') from None

    flat_iter = chain.from_iterable(func(n_range, r))
    indices = np.fromiter(flat_iter, int)
    indices.shape = -1, r
    return a.take(indices, axis, out)


@raise_if(NUMPY_EX)
def fill_diagonal_blocks(array: ndarray, i: int, j: int, val: float = nan) -> None:
    """Fill diagonal blocks in **array** of size :math:`(i, j)`.

    The blocks are filled along the last 2 axes in **array**.
    Performs an inplace update of **array**.

    Examples
    --------
    .. doctest:: python
        :skipif: NUMPY_EX is not None

        >>> import numpy as np
        >>> from nanoutils import fill_diagonal_blocks

        >>> array = np.zeros((10, 15), dtype=int)
        >>> i = 2
        >>> j = 3

        >>> fill_diagonal_blocks(array, i, j, val=1)
        >>> print(array)
        [[1 1 1 0 0 0 0 0 0 0 0 0 0 0 0]
         [1 1 1 0 0 0 0 0 0 0 0 0 0 0 0]
         [0 0 0 1 1 1 0 0 0 0 0 0 0 0 0]
         [0 0 0 1 1 1 0 0 0 0 0 0 0 0 0]
         [0 0 0 0 0 0 1 1 1 0 0 0 0 0 0]
         [0 0 0 0 0 0 1 1 1 0 0 0 0 0 0]
         [0 0 0 0 0 0 0 0 0 1 1 1 0 0 0]
         [0 0 0 0 0 0 0 0 0 1 1 1 0 0 0]
         [0 0 0 0 0 0 0 0 0 0 0 0 1 1 1]
         [0 0 0 0 0 0 0 0 0 0 0 0 1 1 1]]

    Parameters
    ----------
    array : :class:`numpy.ndarray`
        A >= 2D NumPy array whose diagonal blocks are to be filled.
        Gets modified in-place.
    i : :class:`int`
        The size of the diagonal blocks along axis -2.
    j : :class:`int`
        The size of the diagonal blocks along axis -1.
    val : :class:`float`
        Value to be written on the diagonal.
        Its type must be compatible with that of the array **a**.


    :rtype: :data:`None`

    """
    if (j <= 0) or (i <= 0):
        raise ValueError(f"'i' and 'j' should be larger than 0; observed values: {i} & {j}")

    try:
        dim1 = array.shape[-2]
    except IndexError:
        raise ValueError('fill_diagonal_blocks requires an array '
                         'of at least teo dimension') from None
    except (AttributeError, TypeError):
        raise TypeError("fill_diagonal_blocks expected an 'ndarray'; "
                        f"observed type: {array.__class.__name__!r}") from None

    i0 = j0 = 0
    while dim1 > i0:
        array[..., i0:i0+i, j0:j0+j] = val
        i0 += i
        j0 += j


__doc__ = construct_api_doc(globals())
