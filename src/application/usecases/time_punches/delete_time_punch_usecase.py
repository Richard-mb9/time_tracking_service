from application.dtos import RecalculateDailyAttendanceSummaryDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from application.usecases.daily_attendance_summaries import (
    RecalculateDailyAttendanceSummaryUseCase,
)

from .find_time_punch_by_id_usecase import FindTimePunchByIdUseCase


class DeleteTimePunchUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_punch_repository = repository_manager.time_punch_repository()
        self.find_punch_by_id = FindTimePunchByIdUseCase(repository_manager)
        self.recalculate_daily_summary = RecalculateDailyAttendanceSummaryUseCase(
            repository_manager
        )

    def execute(self, punch_id: int, tenant_id: int) -> None:
        punch = self.find_punch_by_id.execute(punch_id=punch_id, raise_if_is_none=True)
        if punch.tenant_id != tenant_id:
            raise BadRequestError("Punch does not belong to tenant.")

        self.time_punch_repository.delete(punch_id)

        self.recalculate_daily_summary.execute(
            RecalculateDailyAttendanceSummaryDTO(
                tenant_id=tenant_id,
                employee_id=punch.employee_id,
                matricula=punch.matricula,
                work_date=punch.punched_at.date(),
            )
        )
