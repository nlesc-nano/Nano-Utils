"""Tests for :mod:`nanoutils.testing_utils`."""

import os
from pathlib import Path

from assertionlib import assertion
from nanoutils import FileNotFoundWarning, delete_finally

PATH = Path('tests') / 'test_files'

DIR1 = PATH / 'tmp_dir'
FILE1 = PATH / 'tmp_file.txt'


def test_warning() -> None:
    """Test :exc:`nanoutils.FileNotFoundWarning`."""
    assertion.issubclass(FileNotFoundWarning, ResourceWarning)


@delete_finally(DIR1, FILE1, warn=False)
def test_delete_finally() -> None:
    """Test :exc:`nanoutils.FileNotFoundWarning`."""
    assertion.isfile(FILE1, invert=True)
    assertion.isdir(DIR1, invert=True)

    os.mkdir(DIR1)
    with open(FILE1, 'w'):
        pass

    assertion.isfile(FILE1)
    assertion.isdir(DIR1)

    @delete_finally(DIR1, FILE1)
    def func() -> None:
        pass

    func()
    assertion.isfile(FILE1, invert=True)
    assertion.isdir(DIR1, invert=True)
