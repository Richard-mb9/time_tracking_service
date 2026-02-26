from datetime import date, datetime
from typing import List, Optional

from application.dtos import CreateTimePunchDTO, RecalculateDailyAttendanceSummaryDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from application.usecases.daily_attendance_summaries import (
    RecalculateDailyAttendanceSummaryUseCase,
)
from application.usecases.employee_enrollments import FindEmployeeEnrollmentByIdUseCase
from domain import TimePunch
from domain.enums import PunchType


class CreateTimePunchUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_punch_repository = repository_manager.time_punch_repository()
        self.employee_enrollment_repository = (
            repository_manager.employee_enrollment_repository()
        )
        self.find_enrollment_by_id = FindEmployeeEnrollmentByIdUseCase(repository_manager)
        self.recalculate_daily_summary = RecalculateDailyAttendanceSummaryUseCase(
            repository_manager
        )

    def execute(self, data: CreateTimePunchDTO) -> TimePunch:
        enrollment = self.find_enrollment_by_id.execute(
            enrollment_id=data.enrollment_id,
            raise_if_is_none=True,
        )

        if enrollment.tenant_id != data.tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")

        self.__validate_active_period(
            active_from=enrollment.active_from,
            active_to=enrollment.active_to,
            is_active=enrollment.is_active,
            punched_at=data.punched_at,
        )

        duplicate = self.time_punch_repository.find_duplicate(
            enrollment_id=data.enrollment_id,
            punched_at=data.punched_at,
            punch_type=data.punch_type,
        )
        if duplicate is not None:
            raise ConflictError("There is already a punch with the same date, time and type.")

        if not data.allow_multi_enrollment_per_day:
            another_enrollments = (
                self.employee_enrollment_repository.find_other_enrollments_with_punch_on_date(
                    tenant_id=data.tenant_id,
                    employee_id=enrollment.employee_id,
                    work_date=data.punched_at.date(),
                    exclude_enrollment_id=enrollment.id,
                )
            )
            if len(another_enrollments) > 0:
                raise BadRequestError(
                    "Employee cannot register punches in multiple enrollments in the same day."
                )

        existing_punches = self.time_punch_repository.find_by_enrollment_and_date(
            enrollment_id=data.enrollment_id,
            work_date=data.punched_at.date(),
        )
        self.__validate_sequence(existing_punches=existing_punches, candidate=data)

        punch = TimePunch(
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            punched_at=data.punched_at,
            punch_type=data.punch_type,
            source=data.source,
            note=data.note,
        )
        created = self.time_punch_repository.create(punch)

        self.recalculate_daily_summary.execute(
            RecalculateDailyAttendanceSummaryDTO(
                tenant_id=data.tenant_id,
                enrollment_id=data.enrollment_id,
                work_date=data.punched_at.date(),
            )
        )

        return created

    def __validate_active_period(
        self,
        active_from: date,
        active_to: Optional[date],
        is_active: bool,
        punched_at: datetime,
    ) -> None:
        if not is_active:
            raise BadRequestError("Inactive enrollment cannot receive punches.")
        punched_date = punched_at.date()
        if punched_date < active_from:
            raise BadRequestError("Punch date is before enrollment active_from.")
        if active_to is not None and punched_date > active_to:
            raise BadRequestError("Punch date is after enrollment active_to.")

    def __validate_sequence(
        self, existing_punches: List[TimePunch], candidate: CreateTimePunchDTO
    ) -> None:
        all_punches: List[TimePunch] = existing_punches + [
            TimePunch(
                tenant_id=candidate.tenant_id,
                enrollment_id=candidate.enrollment_id,
                punched_at=candidate.punched_at,
                punch_type=candidate.punch_type,
                source=candidate.source,
                note=candidate.note,
            )
        ]

        priority = {
            PunchType.IN: 0,
            PunchType.BREAK_START: 1,
            PunchType.BREAK_END: 2,
            PunchType.OUT: 3,
        }

        ordered = sorted(
            all_punches,
            key=lambda punch: (
                punch.punched_at,
                priority[punch.punch_type],
            ),
        )

        inside_shift = False
        in_break = False

        for punch in ordered:
            if punch.punch_type == PunchType.IN:
                if inside_shift:
                    raise BadRequestError("Invalid sequence: IN cannot happen twice in a row.")
                inside_shift = True
                in_break = False
                continue

            if punch.punch_type == PunchType.OUT:
                if not inside_shift:
                    raise BadRequestError("Invalid sequence: OUT requires an open shift.")
                if in_break:
                    raise BadRequestError("Invalid sequence: OUT is not allowed while break is open.")
                inside_shift = False
                continue

            if punch.punch_type == PunchType.BREAK_START:
                if not inside_shift:
                    raise BadRequestError("Invalid sequence: BREAK_START requires IN before it.")
                if in_break:
                    raise BadRequestError("Invalid sequence: BREAK_START already opened.")
                in_break = True
                continue

            if punch.punch_type == PunchType.BREAK_END:
                if not inside_shift:
                    raise BadRequestError("Invalid sequence: BREAK_END requires IN before it.")
                if not in_break:
                    raise BadRequestError("Invalid sequence: BREAK_END requires BREAK_START.")
                in_break = False
