from dataclasses import fields
from typing import Any, cast

from apps.base.typing import TDTO


class BaseDTO:
    """
    Base class for dataclass-based DTOs.

    Subclasses should be decorated with @dataclass (slots=True recommended).
    The empty __slots__ here allows subclasses to fully benefit from slots=True
    without leaving a __dict__ from the base.
    """

    __slots__ = ()

    @classmethod
    def from_dict(cls: type[TDTO], data: dict[str, Any]) -> TDTO:
        """Create an instance from a dictionary, ignoring unknown keys."""
        field_names = {f.name for f in fields(cast('Any', cls))}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
