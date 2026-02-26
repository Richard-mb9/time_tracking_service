from datetime import datetime

from application.dtos import DecideTimeAdjustmentRequestDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from domain import TimeAdjustmentRequest
from domain.enums import TimeAdjustmentStatus

from .find_time_adjustment_request_by_id_usecase import FindTimeAdjustmentRequestByIdUseCase


class DecideTimeAdjustmentRequestUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )
        self.find_request_by_id = FindTimeAdjustmentRequestByIdUseCase(repository_manager)

    def execute(
        self,
        request_id: int,
        tenant_id: int,
        data: DecideTimeAdjustmentRequestDTO,
    ) -> TimeAdjustmentRequest:
        request = self.find_request_by_id.execute(
            request_id=request_id,
            raise_if_is_none=True,
        )

        if request.tenant_id != tenant_id:
            raise BadRequestError("Request does not belong to tenant.")

        if request.status != TimeAdjustmentStatus.PENDING:
            raise BadRequestError("Only pending requests can be decided.")

        if data.status not in [
            TimeAdjustmentStatus.APPROVED,
            TimeAdjustmentStatus.REJECTED,
        ]:
            raise BadRequestError("Decision status must be APPROVED or REJECTED.")

        if data.status == TimeAdjustmentStatus.REJECTED and (
            data.decision_reason is None or len(data.decision_reason.strip()) == 0
        ):
            raise BadRequestError("decision_reason is required for rejection.")

        updated = self.time_adjustment_request_repository.update(
            request_id=request_id,
            data={
                "status": data.status,
                "decided_at": datetime.utcnow(),
                "decided_by_user_id": data.decided_by_user_id,
                "decision_reason": (
                    data.decision_reason.strip() if data.decision_reason is not None else None
                ),
            },
        )

        if updated is None:
            raise BadRequestError("Unable to decide request.")

        return updated
