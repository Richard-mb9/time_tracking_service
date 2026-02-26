from datetime import date
from typing import Optional

from api.schemas import (
    DailyAttendanceSummaryResponse,
    DailyAttendanceStatusRequestEnum,
    PaginatedResponse,
    RecalculateDailyAttendanceSummaryRequest,
)
from application.exceptions import BadRequestError
from application.dtos import (
    ListDailyAttendanceSummariesDTO,
    RecalculateDailyAttendanceSummaryDTO,
)
from application.usecases.daily_attendance_summaries import (
    FindDailyAttendanceSummaryByIdUseCase,
    ListDailyAttendanceSummariesUseCase,
    RecalculateDailyAttendanceSummaryUseCase,
)
from domain import DailyAttendanceSummary
from domain.enums import DailyAttendanceStatus
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class DailyAttendanceSummariesController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def recalculate(
        self, data: RecalculateDailyAttendanceSummaryRequest
    ) -> DailyAttendanceSummaryResponse:
        summary = RecalculateDailyAttendanceSummaryUseCase(self.repository_manager).execute(
            RecalculateDailyAttendanceSummaryDTO(
                tenant_id=data.tenantId,
                employee_id=data.employeeId,
                matricula=data.matricula,
                work_date=data.workDate,
            )
        )
        return self.__to_response(summary)

    def find_by_id(self, summary_id: int, tenant_id: int) -> DailyAttendanceSummaryResponse:
        summary = FindDailyAttendanceSummaryByIdUseCase(self.repository_manager).execute(
            summary_id=summary_id,
            raise_if_is_none=True,
        )
        if summary.tenant_id != tenant_id:
            raise BadRequestError("Summary does not belong to tenant.")
        return self.__to_response(summary)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        employee_id: Optional[int],
        matricula: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date],
        status: Optional[DailyAttendanceStatusRequestEnum],
    ) -> PaginatedResponse[DailyAttendanceSummaryResponse]:
        mapped_status = (
            DailyAttendanceStatus(status.value) if status is not None else None
        )
        result = ListDailyAttendanceSummariesUseCase(self.repository_manager).execute(
            ListDailyAttendanceSummariesDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                employee_id=employee_id,
                matricula=matricula,
                start_date=start_date,
                end_date=end_date,
                status=mapped_status,
            )
        )
        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def __to_response(self, item: DailyAttendanceSummary) -> DailyAttendanceSummaryResponse:
        return DailyAttendanceSummaryResponse(
            id=item.id,
            tenantId=item.tenant_id,
            employeeId=item.employee_id,
            matricula=item.matricula,
            workDate=item.work_date,
            expectedMinutes=item.expected_minutes,
            workedMinutes=item.worked_minutes,
            breakMinutes=item.break_minutes,
            overtimeMinutes=item.overtime_minutes,
            deficitMinutes=item.deficit_minutes,
            status=item.status.value,
        )
