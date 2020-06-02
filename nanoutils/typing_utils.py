""":mod:`typing<python:typing>` related types."""

import sys

if sys.version_info < (3, 8):
    from typing_extensions import Literal, Final, final, Protocol
else:
    from typing import Literal, Final, final, Protocol

__all__ = ['Literal', 'Final', 'final', 'Protocol']
