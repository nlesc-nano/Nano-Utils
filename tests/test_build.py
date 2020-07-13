"""Test building the Nano-Utils package."""

import subprocess

from nanoutils import delete_finally


@delete_finally('dist', 'build')
def test_build() -> None:
    """Test if the package is properly build."""
    subprocess.run('python setup.py sdist bdist_wheel', shell=True, check=True)
