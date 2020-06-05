"""The **Nano-Utils** package."""

# flake8: noqa: F403,F401

from .__version__ import __version__

from . import typing_utils, empty, utils, numpy_utils, schema, set_attr, file_container
from .typing_utils import *
from .empty import *
from .utils import *
from .numpy_utils import *
from .set_attr import *
from .file_container import *
from .schema import (
    Default, Formatter, supports_float, supports_int,
    isinstance_factory, issubclass_factory, import_factory
)

__author__ = 'B. F. van Beek'
__email__ = 'b.f.van.beek@vu.nl'
version_info = VersionInfo.from_str(__version__)

__all__ = []
__all__ += typing_utils.__all__
__all__ += empty.__all__
__all__ += utils.__all__
__all__ += numpy_utils.__all__
__all__ += schema.__all__
__all__ += set_attr.__all__
__all__ += file_container.__all__
