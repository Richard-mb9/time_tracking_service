from application.dtos import ListDailyAttendanceSummariesDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import DailyAttendanceSummary


class ListDailyAttendanceSummariesUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.daily_attendance_summary_repository = (
            repository_manager.daily_attendance_summary_repository()
        )

    def execute(
        self, data: ListDailyAttendanceSummariesDTO
    ) -> PaginatedResult[DailyAttendanceSummary]:
        result = self.daily_attendance_summary_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            start_date=data.start_date,
            end_date=data.end_date,
            status=data.status,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
