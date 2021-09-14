"""Test the :mod:`sphinx` documentation generation."""

from __future__ import annotations

from os.path import join

import pytest
from nanoutils import delete_finally

try:
    from sphinx.application import Sphinx
    SPHINX_EX: None | ImportError = None
except ImportError as ex:
    SPHINX_EX = ex

SRCDIR = CONFDIR = 'docs'
OUTDIR = join('tests', 'test_files', 'build')
DOCTREEDIR = join('tests', 'test_files', 'build', 'doctrees')


@delete_finally(OUTDIR)
@pytest.mark.skipif(SPHINX_EX is not None, reason=str(SPHINX_EX))
def test_sphinx_build() -> None:
    """Test :meth:`sphinx.application.Sphinx.build`."""
    app = Sphinx(SRCDIR, CONFDIR, OUTDIR, DOCTREEDIR,
                 buildername='html', warningiserror=True)
    app.build(force_all=True)
