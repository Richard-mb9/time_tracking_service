from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import DailyAttendanceSummary


class FindDailyAttendanceSummaryByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.daily_attendance_summary_repository = (
            repository_manager.daily_attendance_summary_repository()
        )

    @overload
    def execute(self, summary_id: int) -> Optional[DailyAttendanceSummary]:
        pass

    @overload
    def execute(
        self, summary_id: int, raise_if_is_none: Literal[True]
    ) -> DailyAttendanceSummary:
        pass

    @overload
    def execute(
        self, summary_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[DailyAttendanceSummary]:
        pass

    def execute(self, summary_id: int, raise_if_is_none: bool = False):
        summary = self.daily_attendance_summary_repository.find_by_id(summary_id)
        if raise_if_is_none and summary is None:
            raise NotFoundError("Daily attendance summary not found.")
        return summary
