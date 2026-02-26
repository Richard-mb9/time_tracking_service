from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    data: List[T]
    count: int
    page: int
