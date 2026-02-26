from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginatedResponse(Generic[T]):
    data: List[T]
    count: int
    page: int
