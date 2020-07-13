"""A pytest ``conftest.py`` file."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.config import Config


def pytest_configure(config: 'Config') -> None:
    """Flake8 is very verbose by default. Silence it.

    See Also
    --------
    https://github.com/eisensheng/pytest-catchlog/issues/59

    """
    logging.getLogger("flake8").setLevel(logging.ERROR)
