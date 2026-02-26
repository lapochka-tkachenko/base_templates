from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, TypeVar

if TYPE_CHECKING:
    from apps.base.dto import BaseDTO


TDTO = TypeVar('TDTO', bound='BaseDTO')
AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])
WaitUntil = Literal['commit', 'domcontentloaded', 'load', 'networkidle']
