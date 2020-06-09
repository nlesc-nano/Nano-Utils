"""Tests for :mod:`nanoutils.testing_utils`."""

import os
from pathlib import Path

from assertionlib import assertion
from nanoutils import FileNotFoundWarning, delete_finally

PATH = Path('tests') / 'test_files'


def test_warning() -> None:
    """Test :exc:`nanoutils.FileNotFoundWarning`."""
    assertion.issubclass(FileNotFoundWarning, ResourceWarning)


def test_delete_finally() -> None:
    """Test :exc:`nanoutils.FileNotFoundWarning`."""
    dir1 = PATH / 'tmp_dir'
    file1 = PATH / 'tmp_file.txt'

    os.mkdir(dir1)
    with open(file1, 'w'):
        pass

    assertion.isfile(file1)
    assertion.isdir(dir1)

    @delete_finally(dir1, file1)
    def func() -> None:
        pass

    func()
    assertion.isfile(file1, invert=True)
    assertion.isdir(dir1, invert=True)
