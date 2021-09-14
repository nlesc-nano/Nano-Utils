"""A :class:`yaml.Loader` subclass that dissallows for duplicate keys.

Index
-----
.. currentmodule:: nanoutils
.. autosummary::
    UniqueLoader

API
---
.. autoclass:: UniqueLoader

"""

from __future__ import annotations

from collections.abc import Hashable
from typing import Dict, Any, IO

from .utils import raise_if

try:
    import yaml
    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader  # type: ignore[misc]
    YAML_EX: None | Exception = None
except Exception as ex:
    from builtins import object as Loader  # type: ignore[misc]
    YAML_EX = ex

__all__ = ['UniqueLoader']


class UniqueLoader(Loader):
    '''A :class:`yaml.Loader` subclass that dissallows for duplicate keys.

    Examples
    --------
    .. doctest:: python
        :skipif: YAML_EX is not None

        >>> import yaml
        >>> from nanoutils import UniqueLoader

        >>> STR = """
        ... a: 0
        ... a: 1
        ... """

        >>> yaml.load(STR, Loader=yaml.SafeLoader)
        {'a': 1}

        >>> yaml.load(STR, Loader=UniqueLoader)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
          ...
        yaml.constructor.ConstructorError: while constructing a mapping
          in "<unicode string>", line 2, column 1
        found a duplicate key
          in "<unicode string>", line 3, column 1

    '''

    @raise_if(YAML_EX)  # type: ignore[misc]
    def __init__(cls, stream: str | bytes | IO[str] | IO[bytes]) -> None:
        super().__init__(stream)

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> Dict[Any, Any]:
        """Construct Convert the passed **node** into a :class:`dict`."""
        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(
                None, None, f"expected a mapping node, but found {node.id}", node.start_mark
            )

        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, Hashable):
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "found unhashable key", key_node.start_mark,
                )
            elif key in mapping:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "found a duplicate key", key_node.start_mark,
                )

            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping
