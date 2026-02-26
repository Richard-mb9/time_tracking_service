from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class DBPaginatedResult(Generic[T]):
    data: List[T]
    total_count: int
