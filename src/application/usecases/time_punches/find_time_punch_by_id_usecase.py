from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import TimePunch


class FindTimePunchByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_punch_repository = repository_manager.time_punch_repository()

    @overload
    def execute(self, punch_id: int) -> Optional[TimePunch]:
        pass

    @overload
    def execute(self, punch_id: int, raise_if_is_none: Literal[True]) -> TimePunch:
        pass

    @overload
    def execute(
        self, punch_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[TimePunch]:
        pass

    def execute(self, punch_id: int, raise_if_is_none: bool = False):
        punch = self.time_punch_repository.find_by_id(punch_id)
        if raise_if_is_none and punch is None:
            raise NotFoundError("Time punch not found.")
        return punch
