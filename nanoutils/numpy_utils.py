""":mod:`numpy` related utility functions.

Note that these functions require the numpy package.

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

from math import factorial
from typing import TYPE_CHECKING, Optional, Union, Iterable
from itertools import combinations
from collections import abc

from .utils import raise_if, construct_api_doc

try:
    import numpy as np
    NUMPY_EX: Optional[ImportError] = None
except ImportError as ex:
    NUMPY_EX = ex

if TYPE_CHECKING:
    from numpy import ndarray
    from numpy.typing import DtypeLike, ArrayLike
else:
    DtypeLike = 'numpy.dtype'
    ArrayLike = ndarray = 'numpy.ndarray'

__all__ = ['as_1d_array', 'array_combinations']


@raise_if(NUMPY_EX)
def as_1d_array(value: Union[Iterable, ArrayLike], dtype: DtypeLike, ndmin: int = 1) -> ndarray:
    """Construct a numpy array from an iterable or array-like object.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import as_1d_array

        >>> as_1d_array(1, int)
        array([1])

        >>> as_1d_array([1, 2, 3, 4], int)
        array([1, 2, 3, 4])

        >>> iterator = iter([1, 2, 3, 4])
        >>> as_1d_array(iterator, int)
        array([1, 2, 3, 4])


    Parameters
    ----------
    value : :class:`~collections.abc.Iterable` or array-like
        An array-like object or an iterable consisting of scalars.
    dtype : data-type
        The data type of the to-be returned array.
    ndmin : :class:`int`
        The minimum dimensionality of the to-be returned array.

    Returns
    -------
    :class:`numpy.ndarray`
        A numpy array constructed from **value**.

    """
    try:
        return np.array(value, dtype=dtype, ndmin=ndmin, copy=False)

    except TypeError as ex:
        if not isinstance(value, abc.Iterable):
            raise ex

        ret = np.fromiter(value, dtype=dtype)
        ret.shape += (ndmin - ret.ndim) * (1,)
        return ret


@raise_if(NUMPY_EX)
def array_combinations(array: ArrayLike, r: int = 2, axis: int = -1) -> ndarray:
    r"""Construct an array with all :func:`~itertools.combinations` of **ar** along a use-specified axis.

    Examples
    --------
    .. code:: python

        >>> from nanoutils import array_combinations

        >>> array = [[1, 2, 3, 4],
        ...          [5, 6, 7, 8]]

        >>> array_combinations(array, r=2)
        array([[[1, 2],
                [5, 6]],
        <BLANKLINE>
               [[1, 3],
                [5, 7]],
        <BLANKLINE>
               [[1, 4],
                [5, 8]],
        <BLANKLINE>
               [[2, 3],
                [6, 7]],
        <BLANKLINE>
               [[2, 4],
                [6, 8]],
        <BLANKLINE>
               [[3, 4],
                [7, 8]]])

    Parameters
    ----------
    array : array-like, shape :math:`(m, \dotsc)`
        An :math:`n` dimensional array-like object.
    r : :class:`int`
        The length of each combination.
    axis : :class:`int`
        The axis used for constructing the combinations.

    Returns
    -------
    :class:`numpy.ndarray`, shape :math:`(k, \dotsc, r)`
        A :math:`n+1` dimensional array with all **ar** combinations (of length ``r``)
        along axis -1.
        :math:`k` represents the number of combinations: :math:`k = \dfrac{m! / r!}{(m-r)!}`.

    """  # noqa: E501
    ar = np.array(array, ndmin=1, copy=False)
    n = ar.shape[axis]

    # Identify the number of combinations
    try:
        combinations_len = int(factorial(n) / factorial(r) / factorial(n - r))
    except ValueError as ex:
        raise ValueError(f"'r' ({r!r}) expects a positive integer larger than or equal to the "
                         f"length of 'array' axis {axis!r} ({n!r})") from ex

    # Define the shape of the to-be returned array
    _shape = list(ar.shape)
    del _shape[axis]
    shape = (combinations_len,) + tuple(_shape) + (r,)

    # Create, fill and return the new array
    ret = np.empty(shape, dtype=ar.dtype)
    for i, idx in enumerate(combinations(range(n), r=r)):
        ret[i] = ar.take(idx, axis=axis)
    return ret


__doc__ = construct_api_doc(globals())
