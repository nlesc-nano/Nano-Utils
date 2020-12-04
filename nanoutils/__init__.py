"""The **Nano-Utils** package."""

# flake8: noqa: F403,F401

from .__version__ import __version__

from . import (typing_utils, empty, utils, testing_utils, numpy_utils, schema,
               file_container, hdf5_utils, yaml_utils)
from .typing_utils import *
from .empty import *
from .utils import *
from .testing_utils import *
from .numpy_utils import *
from .file_container import *
from .schema import (
    Default, Formatter, supports_float, supports_int,
    isinstance_factory, issubclass_factory, import_factory
)
from .hdf5_utils import *
from .yaml_utils import *

__author__ = 'B. F. van Beek'
__email__ = 'b.f.van.beek@vu.nl'
version_info = VersionInfo.from_str(__version__)

__all__ = []
__all__ += typing_utils.__all__
__all__ += empty.__all__
__all__ += utils.__all__
__all__ += testing_utils.__all__
__all__ += numpy_utils.__all__
__all__ += schema.__all__
__all__ += file_container.__all__
__all__ += hdf5_utils.__all__
__all__ += yaml_utils.__all__
__all__.sort()
