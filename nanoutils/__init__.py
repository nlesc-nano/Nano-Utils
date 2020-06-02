"""Nano-Utils."""

import os

from .__version__ import __version__

from . import typing_utils, empty, utils, schema
from .typing_utils import *
from .empty import *
from .utils import *
from .schema import *

_README = os.path.join(__path__[0], 'README.rst')  # type: ignore
__doc__ = load_readme(_README, encoding='utf-8')  # type: ignore
del _README
del os

__author__ = 'B. F. van Beek'
__email__ = 'b.f.van.beek@vu.nl'
__version__ = __version__

__all__ = []
__all__ += typing_utils.__all__
__all__ += empty.__all__
__all__ += utils.__all__
__all__ += schema.__all__
