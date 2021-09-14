"""Test building the Nano-Utils package."""

from __future__ import annotations

import subprocess

import pytest
from nanoutils import delete_finally

try:
    import wheel  # noqa: F401
    WHEEL_EX: None | ImportError = None
except ImportError as ex:
    WHEEL_EX = ex


@delete_finally('dist', 'build')
@pytest.mark.skipif(WHEEL_EX is not None, reason=str(WHEEL_EX))
def test_build() -> None:
    """Test if the package is properly build."""
    subprocess.run('python setup.py sdist bdist_wheel', shell=True, check=True)
