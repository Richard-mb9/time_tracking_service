from typing import List, Set, Tuple

from application.dtos import CreateTimeAdjustmentRequestDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from application.usecases.time_punches import FindTimePunchByIdUseCase
from domain import TimeAdjustmentItem, TimeAdjustmentRequest


class CreateTimeAdjustmentRequestUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )
        self.time_adjustment_item_repository = (
            repository_manager.time_adjustment_item_repository()
        )
        self.find_time_punch_by_id = FindTimePunchByIdUseCase(repository_manager)

    def execute(self, data: CreateTimeAdjustmentRequestDTO) -> TimeAdjustmentRequest:
        matricula = data.matricula.strip()
        if len(matricula) == 0:
            raise BadRequestError("matricula is required.")

        if len(data.reason.strip()) == 0:
            raise BadRequestError("reason is required.")

        if len(data.items) == 0:
            raise BadRequestError("At least one adjustment item is required.")

        fingerprints: Set[Tuple[str, str, str]] = set()

        for item in data.items:
            if item.original_punch_id is None:
                if item.proposed_punch_type is None or item.proposed_punched_at is None:
                    raise BadRequestError(
                        "New punch adjustments require proposed_punch_type and proposed_punched_at."
                    )
            else:
                original_punch = self.find_time_punch_by_id.execute(
                    punch_id=item.original_punch_id,
                    raise_if_is_none=True,
                )
                if (
                    original_punch.employee_id != data.employee_id
                    or original_punch.matricula != matricula
                ):
                    raise BadRequestError(
                        "original_punch_id does not belong to employee and matricula."
                    )

            if item.proposed_punched_at is not None and item.proposed_punched_at.date() != data.request_date:
                raise BadRequestError("All proposed punches must match request_date.")

            fingerprint = (
                str(item.proposed_punch_type.value if item.proposed_punch_type is not None else None),
                str(item.proposed_punched_at.isoformat() if item.proposed_punched_at else None),
                str(item.original_punch_id),
            )
            if fingerprint in fingerprints:
                raise BadRequestError("Duplicate adjustment item detected.")
            fingerprints.add(fingerprint)

        request = TimeAdjustmentRequest(
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=matricula,
            request_date=data.request_date,
            request_type=data.request_type,
            reason=data.reason.strip(),
            requester_user_id=data.requester_user_id,
        )

        created_request = self.time_adjustment_request_repository.create(request)

        request_items = [
            TimeAdjustmentItem(
                tenant_id=data.tenant_id,
                request_id=created_request.id,
                proposed_punch_type=item.proposed_punch_type,
                proposed_punched_at=item.proposed_punched_at,
                original_punch_id=item.original_punch_id,
                note=item.note,
            )
            for item in data.items
        ]
        self.time_adjustment_item_repository.create_many(request_items)

        return created_request
