from functools import partial
from typing import Generic, Any, TypeVar, List

__all__: List[str] = ...

_T = TypeVar('_T')


class PartialPrepend(partial[_T]):
    def __call__(self, *args: Any, **keywords: Any) -> _T:
        ...
