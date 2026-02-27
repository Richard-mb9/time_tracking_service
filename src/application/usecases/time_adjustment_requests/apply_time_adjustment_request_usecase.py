from collections import defaultdict
from datetime import date
from typing import Dict, List, Set

from application.dtos import RecalculateDailyAttendanceSummaryDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from application.usecases.daily_attendance_summaries import (
    RecalculateDailyAttendanceSummaryUseCase,
)
from application.usecases.time_punches import FindTimePunchByIdUseCase
from domain import TimeAdjustmentRequest, TimePunch
from domain.enums import PunchType, TimeAdjustmentStatus

from .find_time_adjustment_request_by_id_usecase import (
    FindTimeAdjustmentRequestByIdUseCase,
)


class ApplyTimeAdjustmentRequestUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )
        self.time_adjustment_item_repository = (
            repository_manager.time_adjustment_item_repository()
        )
        self.time_punch_repository = repository_manager.time_punch_repository()
        self.find_request_by_id = FindTimeAdjustmentRequestByIdUseCase(
            repository_manager
        )
        self.find_punch_by_id = FindTimePunchByIdUseCase(repository_manager)
        self.recalculate_daily_summary = RecalculateDailyAttendanceSummaryUseCase(
            repository_manager
        )

    def execute(self, request_id: int, tenant_id: int) -> TimeAdjustmentRequest:
        request = self.find_request_by_id.execute(
            request_id=request_id,
            raise_if_is_none=True,
        )

        if request.tenant_id != tenant_id:
            raise BadRequestError("Request does not belong to tenant.")

        if request.status == TimeAdjustmentStatus.APPLIED:
            return request

        if request.status != TimeAdjustmentStatus.APPROVED:
            raise BadRequestError("Only approved requests can be applied.")

        items = self.time_adjustment_item_repository.find_by_request_id(request_id)
        if len(items) == 0:
            raise BadRequestError("No adjustment items found for request.")

        affected_dates = self.__resolve_affected_dates(
            request.employee_id,
            request.matricula,
            items,
        )
        self.__validate_final_sequences(
            request.employee_id,
            request.matricula,
            items,
            affected_dates,
        )

        for item in items:
            if item.original_punch_id is not None:
                original_punch = self.find_punch_by_id.execute(
                    punch_id=item.original_punch_id,
                    raise_if_is_none=True,
                )
                if (
                    original_punch.employee_id != request.employee_id
                    or original_punch.matricula != request.matricula
                ):
                    raise BadRequestError(
                        "original_punch_id does not belong to employee and matricula."
                    )

                if (
                    item.proposed_punch_type is not None
                    and item.proposed_punched_at is not None
                ):
                    self.time_punch_repository.update(
                        punch_id=original_punch.id,
                        data={
                            "punched_at": item.proposed_punched_at,
                            "punch_type": item.proposed_punch_type,
                            "note": item.note,
                        },
                    )
                else:
                    self.time_punch_repository.delete(original_punch.id)
                continue

            if item.proposed_punch_type is None or item.proposed_punched_at is None:
                raise BadRequestError("Invalid adjustment item for new punch.")

            self.time_punch_repository.create(
                TimePunch(
                    tenant_id=request.tenant_id,
                    employee_id=request.employee_id,
                    matricula=request.matricula,
                    punched_at=item.proposed_punched_at,
                    punch_type=item.proposed_punch_type,
                    source="adjustment",
                    note=item.note,
                )
            )

        updated_request = self.time_adjustment_request_repository.update(
            request_id=request_id,
            data={"status": TimeAdjustmentStatus.APPLIED},
        )
        if updated_request is None:
            raise BadRequestError("Unable to apply request.")

        for affected_date in affected_dates:
            self.recalculate_daily_summary.execute(
                RecalculateDailyAttendanceSummaryDTO(
                    tenant_id=request.tenant_id,
                    employee_id=request.employee_id,
                    matricula=request.matricula,
                    work_date=affected_date,
                )
            )

        return updated_request

    def __resolve_affected_dates(
        self, employee_id: int, matricula: str, items: List
    ) -> Set[date]:
        affected_dates: Set[date] = set()

        for item in items:
            if item.proposed_punched_at is not None:
                affected_dates.add(item.proposed_punched_at.date())

            if item.original_punch_id is not None:
                original_punch = self.find_punch_by_id.execute(
                    punch_id=item.original_punch_id,
                    raise_if_is_none=True,
                )
                if (
                    original_punch.employee_id != employee_id
                    or original_punch.matricula != matricula
                ):
                    raise BadRequestError(
                        "original_punch_id does not belong to employee and matricula."
                    )
                affected_dates.add(original_punch.punched_at.date())

        return affected_dates

    def __validate_final_sequences(
        self,
        employee_id: int,
        matricula: str,
        items: List,
        affected_dates: Set[date],
    ) -> None:
        by_date = defaultdict(list)

        for affected_date in affected_dates:
            punches = (
                self.time_punch_repository.find_by_employee_and_matricula_and_date(
                    employee_id=employee_id,
                    matricula=matricula,
                    work_date=affected_date,
                )
            )
            by_date[affected_date] = punches[:]

        for item in items:
            if item.original_punch_id is not None:
                original_punch = self.find_punch_by_id.execute(
                    punch_id=item.original_punch_id,
                    raise_if_is_none=True,
                )
                if (
                    original_punch.employee_id != employee_id
                    or original_punch.matricula != matricula
                ):
                    raise BadRequestError(
                        "original_punch_id does not belong to employee and matricula."
                    )
                original_date = original_punch.punched_at.date()
                by_date[original_date] = [
                    punch
                    for punch in by_date[original_date]
                    if punch.id != original_punch.id
                ]

                if (
                    item.proposed_punch_type is not None
                    and item.proposed_punched_at is not None
                ):
                    by_date[item.proposed_punched_at.date()].append(
                        TimePunch(
                            tenant_id=original_punch.tenant_id,
                            employee_id=original_punch.employee_id,
                            matricula=original_punch.matricula,
                            punched_at=item.proposed_punched_at,
                            punch_type=item.proposed_punch_type,
                            source=original_punch.source,
                            note=item.note,
                        )
                    )
                continue

            if (
                item.proposed_punch_type is not None
                and item.proposed_punched_at is not None
            ):
                by_date[item.proposed_punched_at.date()].append(
                    TimePunch(
                        tenant_id=0,
                        employee_id=employee_id,
                        matricula=matricula,
                        punched_at=item.proposed_punched_at,
                        punch_type=item.proposed_punch_type,
                        source="adjustment",
                        note=item.note,
                    )
                )

        for date_punches in by_date.values():
            self.__validate_sequence(date_punches)

    def __validate_sequence(self, punches: List[TimePunch]) -> None:
        priority = {
            PunchType.IN: 0,
            PunchType.OUT: 1,
        }
        ordered = sorted(
            punches,
            key=lambda punch: (
                punch.punched_at,
                priority[
                    PunchType(punch.punch_type)
                    if isinstance(punch.punch_type, str)
                    else punch.punch_type
                ],
            ),
        )

        inside_shift = False

        for punch in ordered:
            punch_type = (
                PunchType(punch.punch_type)
                if isinstance(punch.punch_type, str)
                else punch.punch_type
            )

            if punch_type == PunchType.IN:
                if inside_shift:
                    raise BadRequestError("Invalid resulting sequence for adjustment.")
                inside_shift = True
                continue

            if punch_type == PunchType.OUT:
                if not inside_shift:
                    raise BadRequestError("Invalid resulting sequence for adjustment.")
                inside_shift = False
