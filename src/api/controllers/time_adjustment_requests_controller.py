from datetime import date
from typing import Optional

from api.routers.dependencies.access_token_data import AccessTokenData
from api.schemas import (
    CreateTimeAdjustmentRequest,
    DecideTimeAdjustmentRequest,
    DefaultCreateResponse,
    PaginatedResponse,
    TimeAdjustmentItemResponse,
    TimeAdjustmentRequestResponse,
    TimeAdjustmentStatusRequestEnum,
)
from application.exceptions import BadRequestError
from application.dtos import (
    CreateTimeAdjustmentItemDTO,
    CreateTimeAdjustmentRequestDTO,
    DecideTimeAdjustmentRequestDTO,
    ListTimeAdjustmentRequestsDTO,
)
from application.usecases.time_adjustment_requests import (
    ApplyTimeAdjustmentRequestUseCase,
    CreateTimeAdjustmentRequestUseCase,
    DecideTimeAdjustmentRequestUseCase,
    DeleteTimeAdjustmentRequestUseCase,
    FindTimeAdjustmentRequestByIdUseCase,
    ListTimeAdjustmentRequestsUseCase,
)
from domain import TimeAdjustmentItem, TimeAdjustmentRequest
from domain.enums import PunchType, TimeAdjustmentStatus, TimeAdjustmentType
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class TimeAdjustmentRequestsController:
    def __init__(
        self,
        db_manager: DatabaseManagerConnection,
        access_token: Optional[AccessTokenData] = None,
    ):
        self.repository_manager = RepositoryManager(db_manager=db_manager)
        self.access_token = access_token

    @property
    def _requesting_user_id(self) -> Optional[int]:
        return self.access_token.user_id if self.access_token else None

    def create(self, data: CreateTimeAdjustmentRequest) -> DefaultCreateResponse:
        request = CreateTimeAdjustmentRequestUseCase(self.repository_manager).execute(
            CreateTimeAdjustmentRequestDTO(
                tenant_id=data.tenantId,
                employee_id=data.employeeId,
                matricula=data.matricula,
                request_date=data.requestDate,
                request_type=TimeAdjustmentType(data.requestType.value),
                reason=data.reason,
                requester_user_id=data.requesterUserId,
                items=[
                    CreateTimeAdjustmentItemDTO(
                        proposed_punch_type=(
                            PunchType(item.proposedPunchType.value)
                            if item.proposedPunchType is not None
                            else None
                        ),
                        proposed_punched_at=item.proposedPunchedAt,
                        original_punch_id=item.originalPunchId,
                        note=item.note,
                    )
                    for item in data.items
                ],
            )
        )
        return DefaultCreateResponse(id=request.id)

    def find_by_id(self, request_id: int, tenant_id: int) -> TimeAdjustmentRequestResponse:
        request = FindTimeAdjustmentRequestByIdUseCase(self.repository_manager).execute(
            request_id=request_id,
            raise_if_is_none=True,
        )
        if request.tenant_id != tenant_id:
            raise BadRequestError("Request does not belong to tenant.")
        return self.__to_response(request)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        employee_id: Optional[int],
        matricula: Optional[str],
        status: Optional[TimeAdjustmentStatusRequestEnum],
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> PaginatedResponse[TimeAdjustmentRequestResponse]:
        mapped_status = (
            TimeAdjustmentStatus(status.value) if status is not None else None
        )
        result = ListTimeAdjustmentRequestsUseCase(self.repository_manager).execute(
            ListTimeAdjustmentRequestsDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                employee_id=employee_id,
                matricula=matricula,
                status=mapped_status,
                start_date=start_date,
                end_date=end_date,
            )
        )
        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def decide(
        self,
        request_id: int,
        tenant_id: int,
        data: DecideTimeAdjustmentRequest,
    ) -> TimeAdjustmentRequestResponse:
        request = DecideTimeAdjustmentRequestUseCase(self.repository_manager).execute(
            request_id=request_id,
            tenant_id=tenant_id,
            data=DecideTimeAdjustmentRequestDTO(
                status=TimeAdjustmentStatus(data.status.value),
                decided_by_user_id=data.decidedByUserId,
                decision_reason=data.decisionReason,
            ),
        )
        return self.__to_response(request)

    def apply(self, request_id: int, tenant_id: int) -> TimeAdjustmentRequestResponse:
        request = ApplyTimeAdjustmentRequestUseCase(self.repository_manager).execute(
            request_id=request_id,
            tenant_id=tenant_id,
        )
        return self.__to_response(request)

    def delete(self, request_id: int, tenant_id: int) -> None:
        DeleteTimeAdjustmentRequestUseCase(self.repository_manager).execute(
            request_id=request_id,
            tenant_id=tenant_id,
        )

    def __to_response(self, request: TimeAdjustmentRequest) -> TimeAdjustmentRequestResponse:
        return TimeAdjustmentRequestResponse(
            id=request.id,
            tenantId=request.tenant_id,
            employeeId=request.employee_id,
            matricula=request.matricula,
            requestDate=request.request_date,
            requestType=request.request_type.value,
            status=request.status.value,
            reason=request.reason,
            requesterUserId=request.requester_user_id,
            decidedAt=request.decided_at,
            decidedByUserId=request.decided_by_user_id,
            decisionReason=request.decision_reason,
            items=[self.__to_item_response(item) for item in (request.items or [])],
        )

    def __to_item_response(self, item: TimeAdjustmentItem) -> TimeAdjustmentItemResponse:
        return TimeAdjustmentItemResponse(
            id=item.id,
            requestId=item.request_id,
            proposedPunchType=(
                item.proposed_punch_type.value
                if item.proposed_punch_type is not None
                else None
            ),
            proposedPunchedAt=item.proposed_punched_at,
            originalPunchId=item.original_punch_id,
            note=item.note,
        )
