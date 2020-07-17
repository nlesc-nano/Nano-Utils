#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""Print :code:`TRUE` if the :mod:`numpy` version is 1.20 or higher; print :code:`FALSE` otherwise.

Examples
--------
.. code:: bash

    >>> pip show numpy  # doctest: +SKIP
    Name: numpy
    Version: 1.17.3
    Summary: NumPy is the fundamental package for array computing with Python.
    Home-page: https://www.numpy.org
    ...

    >>> python ./numpy_ge_1_20.py  # doctest: +SKIP
    FALSE

"""  # noqa: E501

import warnings
from typing import Optional

from nanoutils import VersionInfo

try:
    import numpy as np
    NUMPY_EX: Optional[ImportError] = None
except ImportError as ex:
    NUMPY_EX = ex


def main() -> None:
    """Execute the script."""
    __version__: Optional[str] = getattr(np, '__version__', None)

    try:
        major, minor, micro, *_ = __version__.split('.')  # type: ignore
        version = VersionInfo(major=int(major), minor=int(minor), micro=int(micro))
    except Exception as ex:
        warning = RuntimeWarning(f"Failed to parse the NumPy version: {__version__!r}")
        warning.__cause__ = ex
        warnings.warn(warning)
        return

    if version.major > 1 or (version.major == 1 and version.minor >= 20):
        print("TRUE")
    else:
        print("FALSE")


if __name__ == '__main__':
    if NUMPY_EX is not None:
        _warning = ImportWarning(str(NUMPY_EX))
        _warning.__cause__ = NUMPY_EX
        warnings.warn(_warning)
        del _warning
    else:
        main()
