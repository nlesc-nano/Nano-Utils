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

import warnings
from math import factorial, nan
from typing import TYPE_CHECKING, Optional, Union, Iterable
from itertools import combinations
from collections import abc

from .utils import raise_if, construct_api_doc, VersionInfo

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

__all__ = ['as_nd_array', 'array_combinations', 'fill_diagonal_blocks']


@raise_if(NUMPY_EX)
def as_nd_array(array: Union[Iterable, ArrayLike], dtype: DtypeLike,
                ndmin: int = 1, copy: bool = False) -> ndarray:
    """Construct a numpy array from an iterable or array-like object.

    Examples
    --------
    .. code:: python

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
        along the user-specified **axis**.
        The variable :math:`k` herein represents the number of combinations:
        :math:`k = \dfrac{m! / r!}{(m-r)!}`.

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


@raise_if(NUMPY_EX)
def fill_diagonal_blocks(array: ndarray, i: int, j: int, val: float = nan) -> None:
    """Fill diagonal blocks in **array** of size :math:`(i, j)`.

    The blocks are filled along the last 2 axes in **array**.
    Performs an inplace update of **array**.

    Examples
    --------
    .. code:: python

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

    i0 = j0 = 0
    dim1 = array.shape[-2]
    while dim1 > i0:
        array[..., i0:i0+i, j0:j0+j] = val
        i0 += i
        j0 += j


def numpy_ge_1_20() -> None:
    r"""Print :code:`"\nnumpy >= 1.20: TRUE"` if the :mod:`numpy` version is 1.20 or higher; print :code:`"\nnumpy >= 1.20: FALSE"` otherwise.

    :code:`"\nnumpy >= 1.20: ERROR"` will be printed if an exception is encountered.

    Examples
    --------
    .. code:: python

        >>> import numpy as np
        >>> from nanoutils.numpy_utils import numpy_ge_1_20

        >>> np.__version__  # doctest: +SKIP
        '1.17.3'

        >>> numpy_ge_1_20()  # doctest: +SKIP
        <BLANKLINE>
        numpy >= 1.20: FALSE

    A command line example.

    .. code:: bash

        >>> pip show numpy  # doctest: +SKIP
        Name: numpy
        Version: 1.17.3
        Summary: NumPy is the fundamental package for array computing with Python.
        Home-page: https://www.numpy.org
        ...

        >>> numpy_ge_1_20  # doctest: +SKIP
        <BLANKLINE>
        numpy >= 1.20: FALSE

    """  # noqa: E501
    if NUMPY_EX is not None:
        warning1 = ImportWarning(str(NUMPY_EX))
        warning1.__cause__ = NUMPY_EX
        warnings.warn(warning1)
        print("\nnumpy >= 1.20: ERROR")
        return

    __version__ = getattr(np, '__version__', None)
    try:
        version = VersionInfo.from_str(__version__)
    except Exception as ex:
        warning2 = RuntimeWarning(f"Failed to parse the NumPy version: {__version__!r}")
        warning2.__cause__ = ex
        warnings.warn(warning2)
        print("\nnumpy >= 1.20: ERROR")
        return

    if version.major > 1 or (version.major == 1 and version.minor >= 20):
        print("\nnumpy >= 1.20: TRUE")
    else:
        print("\nnumpy >= 1.20: FALSE")


__doc__ = construct_api_doc(globals())
