""":mod:`typing<python:typing>` related types.

Contains aliases for ``python >= 3.8`` exclusive objects related to typing.

Index
-----
========================= ===================================================================
:data:`~typing.Literal`   Special typing form to define literal types (a.k.a. value types).
:data:`~typing.Final`     Special typing construct to indicate final names to type checkers.
:func:`~typing.final`     A decorator to indicate final methods and final classes.
:class:`~typing.Protocol` Base class for protocol classes.
========================= ===================================================================

"""

import sys

if sys.version_info < (3, 8):
    from typing_extensions import Literal, Final, final, Protocol
else:
    from typing import Literal, Final, final, Protocol

__all__ = ['Literal', 'Final', 'final', 'Protocol']
