from datetime import datetime
from typing import List

from application.dtos import CreateTimePunchDTO, RecalculateDailyAttendanceSummaryDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from application.usecases.daily_attendance_summaries import (
    RecalculateDailyAttendanceSummaryUseCase,
)
from application.usecases.enrollment_policy_assignments import (
    FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase,
)
from domain import TimePunch
from domain.enums import PunchType


class CreateTimePunchUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_punch_repository = repository_manager.time_punch_repository()
        self.recalculate_daily_summary = RecalculateDailyAttendanceSummaryUseCase(
            repository_manager
        )
        self.find_assignment_by_date = (
            FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase(repository_manager)
        )

    def execute(self, data: CreateTimePunchDTO) -> TimePunch:
        matricula = data.matricula.strip()
        if len(matricula) == 0:
            raise BadRequestError("matricula is required.")

        assignment = self.find_assignment_by_date.execute(
            employee_id=data.employee_id,
            matricula=matricula,
            reference_date=data.punched_at.date(),
        )
        if assignment is None:
            raise BadRequestError("Employee does not have a work policy assignment for this date.")

        duplicate = self.time_punch_repository.find_duplicate(
            employee_id=data.employee_id,
            matricula=matricula,
            punched_at=data.punched_at,
            punch_type=data.punch_type,
        )
        if duplicate is not None:
            raise ConflictError("There is already a punch with the same date, time and type.")

        if not data.allow_multi_enrollment_per_day:
            punches_in_other_matriculas = (
                self.time_punch_repository.find_other_matriculas_with_punch_on_date(
                    tenant_id=data.tenant_id,
                    employee_id=data.employee_id,
                    work_date=data.punched_at.date(),
                    matricula_to_exclude=matricula,
                )
            )
            if len(punches_in_other_matriculas) > 0:
                raise BadRequestError(
                    "Employee cannot register punches in multiple matriculas in the same day."
                )

        existing_punches = self.time_punch_repository.find_by_employee_and_matricula_and_date(
            employee_id=data.employee_id,
            matricula=matricula,
            work_date=data.punched_at.date(),
        )
        self.__validate_sequence(existing_punches=existing_punches, candidate=data, matricula=matricula)

        punch = TimePunch(
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=matricula,
            punched_at=data.punched_at,
            punch_type=data.punch_type,
            source=data.source,
            note=data.note,
        )
        created = self.time_punch_repository.create(punch)

        self.recalculate_daily_summary.execute(
            RecalculateDailyAttendanceSummaryDTO(
                tenant_id=data.tenant_id,
                employee_id=data.employee_id,
                matricula=matricula,
                work_date=data.punched_at.date(),
            )
        )

        return created

    def __validate_sequence(
        self, existing_punches: List[TimePunch], candidate: CreateTimePunchDTO, matricula: str
    ) -> None:
        all_punches: List[TimePunch] = existing_punches + [
            TimePunch(
                tenant_id=candidate.tenant_id,
                employee_id=candidate.employee_id,
                matricula=matricula,
                punched_at=candidate.punched_at,
                punch_type=candidate.punch_type,
                source=candidate.source,
                note=candidate.note,
            )
        ]

        priority = {
            PunchType.IN: 0,
            PunchType.OUT: 1,
        }

        ordered = sorted(
            all_punches,
            key=lambda punch: (
                punch.punched_at,
                priority[punch.punch_type],
            ),
        )

        inside_shift = False
        for punch in ordered:
            if punch.punch_type == PunchType.IN:
                if inside_shift:
                    raise BadRequestError("Invalid sequence: IN cannot happen twice in a row.")
                inside_shift = True
                continue

            if punch.punch_type == PunchType.OUT:
                if not inside_shift:
                    raise BadRequestError("Invalid sequence: OUT requires an open shift.")
                inside_shift = False
