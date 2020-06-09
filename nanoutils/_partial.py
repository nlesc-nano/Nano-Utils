"""A private module for containg the :class:`nanoutils.PartialPrepend` class.

Notes
-----
:class:`~nanoutils.PartialPrepend` should be imported from
either :mod:`nanoutils` or :mod:`nanoutils.utils`.

"""

from typing import List
from functools import partial

__all__: List[str] = []


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
