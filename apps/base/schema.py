from dataclasses import fields
from typing import Any, cast

from apps.base.typing import TSchema


class BaseSchema:
    """
    Base schema class providing helper methods for dataclass-like schemas.
    """

    @classmethod
    def from_dict(cls: type[TSchema], data: dict[str, Any]) -> TSchema:
        """
        Create an instance of the schema from a dictionary.
        """
        field_names = {f.name for f in fields(cast('Any', cls))}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
