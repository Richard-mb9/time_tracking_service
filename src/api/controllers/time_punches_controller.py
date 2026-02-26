from datetime import datetime
from typing import Optional

from api.schemas import (
    CreateTimePunchRequest,
    DefaultCreateResponse,
    PaginatedResponse,
    PunchTypeRequestEnum,
    TimePunchResponse,
)
from application.exceptions import BadRequestError
from application.dtos import CreateTimePunchDTO, ListTimePunchesDTO
from application.usecases.time_punches import (
    CreateTimePunchUseCase,
    DeleteTimePunchUseCase,
    FindTimePunchByIdUseCase,
    ListTimePunchesUseCase,
)
from domain import TimePunch
from domain.enums import PunchType
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class TimePunchesController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateTimePunchRequest) -> DefaultCreateResponse:
        punch = CreateTimePunchUseCase(self.repository_manager).execute(
            CreateTimePunchDTO(
                tenant_id=data.tenantId,
                enrollment_id=data.enrollmentId,
                punched_at=data.punchedAt,
                punch_type=PunchType(data.punchType.value),
                source=data.source,
                note=data.note,
                allow_multi_enrollment_per_day=data.allowMultiEnrollmentPerDay,
            )
        )
        return DefaultCreateResponse(id=punch.id)

    def find_by_id(self, punch_id: int, tenant_id: int) -> TimePunchResponse:
        punch = FindTimePunchByIdUseCase(self.repository_manager).execute(
            punch_id=punch_id,
            raise_if_is_none=True,
        )
        if punch.tenant_id != tenant_id:
            raise BadRequestError("Punch does not belong to tenant.")
        return self.__to_response(punch)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        enrollment_id: Optional[int],
        start_at: Optional[datetime],
        end_at: Optional[datetime],
        punch_type: Optional[PunchTypeRequestEnum],
    ) -> PaginatedResponse[TimePunchResponse]:
        mapped_punch_type = (
            PunchType(punch_type.value) if punch_type is not None else None
        )
        result = ListTimePunchesUseCase(self.repository_manager).execute(
            ListTimePunchesDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                enrollment_id=enrollment_id,
                start_at=start_at,
                end_at=end_at,
                punch_type=mapped_punch_type,
            )
        )

        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def delete(self, punch_id: int, tenant_id: int) -> None:
        DeleteTimePunchUseCase(self.repository_manager).execute(
            punch_id=punch_id,
            tenant_id=tenant_id,
        )

    def __to_response(self, item: TimePunch) -> TimePunchResponse:
        return TimePunchResponse(
            id=item.id,
            tenantId=item.tenant_id,
            enrollmentId=item.enrollment_id,
            punchedAt=item.punched_at,
            punchType=item.punch_type.value,
            source=item.source,
            note=item.note,
        )
