from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from apps.base.dto import BaseDTO


TDTO = TypeVar('TDTO', bound='BaseDTO')
AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])
