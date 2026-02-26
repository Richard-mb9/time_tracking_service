from typing import Any
from enum import Enum


def get_enum_value(item: Any) -> Any:
    if isinstance(item, Enum):
        return item.value
    return item
