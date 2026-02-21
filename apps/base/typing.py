from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from apps.base.schema import BaseSchema


TSchema = TypeVar('TSchema', bound='BaseSchema')
