from datetime import date, datetime
from typing import List, Optional, Tuple

from application.dtos import RecalculateDailyAttendanceSummaryDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from application.usecases.employee_enrollments import FindEmployeeEnrollmentByIdUseCase
from application.usecases.enrollment_policy_assignments import (
    FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase,
)
from domain import BankHoursLedger, DailyAttendanceSummary, TimePunch
from domain.enums import (
    BankHoursSource,
    DailyAttendanceStatus,
    PunchType,
    TimeAdjustmentStatus,
)


class RecalculateDailyAttendanceSummaryUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.daily_attendance_summary_repository = (
            repository_manager.daily_attendance_summary_repository()
        )
        self.time_punch_repository = repository_manager.time_punch_repository()
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )
        self.bank_hours_ledger_repository = repository_manager.bank_hours_ledger_repository()
        self.find_enrollment_by_id = FindEmployeeEnrollmentByIdUseCase(repository_manager)
        self.find_assignment_by_date = (
            FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase(repository_manager)
        )

    def execute(self, data: RecalculateDailyAttendanceSummaryDTO) -> DailyAttendanceSummary:
        enrollment = self.find_enrollment_by_id.execute(
            enrollment_id=data.enrollment_id,
            raise_if_is_none=True,
        )
        if enrollment.tenant_id != data.tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")

        assignment = self.find_assignment_by_date.execute(
            enrollment_id=data.enrollment_id,
            reference_date=data.work_date,
        )

        punches = self.time_punch_repository.find_by_enrollment_and_date(
            enrollment_id=data.enrollment_id,
            work_date=data.work_date,
        )
        worked_minutes, break_minutes, is_complete = self.__calculate_minutes(punches)

        expected_minutes = (
            assignment.template.daily_work_minutes if assignment is not None else 0
        )
        has_pending_adjustment = self.__has_pending_adjustment(
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            work_date=data.work_date,
        )
        status = self.__resolve_status(
            assignment_exists=assignment is not None,
            has_pending_adjustment=has_pending_adjustment,
            is_complete=is_complete,
            punches_count=len(punches),
        )

        overtime_minutes = 0
        deficit_minutes = 0
        if status == DailyAttendanceStatus.OK:
            if worked_minutes > expected_minutes:
                overtime_minutes = worked_minutes - expected_minutes
            elif worked_minutes < expected_minutes:
                deficit_minutes = expected_minutes - worked_minutes

        summary = DailyAttendanceSummary(
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            work_date=data.work_date,
            expected_minutes=expected_minutes,
            worked_minutes=worked_minutes,
            break_minutes=break_minutes,
            overtime_minutes=overtime_minutes,
            deficit_minutes=deficit_minutes,
            status=status,
        )

        persisted_summary = self.daily_attendance_summary_repository.upsert(summary)

        self.bank_hours_ledger_repository.delete_auto_generated_for_day(
            enrollment_id=data.enrollment_id,
            event_date=data.work_date,
            source=BankHoursSource.DAILY_APURATION,
        )

        daily_delta = overtime_minutes - deficit_minutes
        if status == DailyAttendanceStatus.OK and daily_delta != 0:
            self.bank_hours_ledger_repository.create(
                BankHoursLedger(
                    tenant_id=data.tenant_id,
                    enrollment_id=data.enrollment_id,
                    event_date=data.work_date,
                    minutes_delta=daily_delta,
                    source=BankHoursSource.DAILY_APURATION,
                    reference_id=persisted_summary.id,
                )
            )

        return persisted_summary

    def __has_pending_adjustment(
        self, tenant_id: int, enrollment_id: int, work_date: date
    ) -> bool:
        result = self.time_adjustment_request_repository.find_all(
            page=0,
            per_page=1,
            tenant_id=tenant_id,
            enrollment_id=enrollment_id,
            status=TimeAdjustmentStatus.PENDING,
            start_date=work_date,
            end_date=work_date,
        )
        return result.total_count > 0

    def __resolve_status(
        self,
        assignment_exists: bool,
        has_pending_adjustment: bool,
        is_complete: bool,
        punches_count: int,
    ) -> DailyAttendanceStatus:
        if not assignment_exists:
            return DailyAttendanceStatus.NO_POLICY
        if has_pending_adjustment:
            return DailyAttendanceStatus.PENDING_ADJUSTMENT
        if not is_complete:
            return DailyAttendanceStatus.INCOMPLETE
        if punches_count == 0:
            return DailyAttendanceStatus.INCOMPLETE
        return DailyAttendanceStatus.OK

    def __calculate_minutes(self, punches: List[TimePunch]) -> Tuple[int, int, bool]:
        ordered = sorted(punches, key=lambda punch: punch.punched_at)

        worked_minutes = 0
        break_minutes = 0

        open_interval_start: Optional[datetime] = None
        open_break_start: Optional[datetime] = None

        for punch in ordered:
            if punch.punch_type == PunchType.IN:
                if open_interval_start is not None or open_break_start is not None:
                    return 0, 0, False
                open_interval_start = punch.punched_at
                continue

            if punch.punch_type == PunchType.BREAK_START:
                if open_interval_start is None or open_break_start is not None:
                    return 0, 0, False
                worked_minutes += self.__diff_in_minutes(open_interval_start, punch.punched_at)
                open_interval_start = None
                open_break_start = punch.punched_at
                continue

            if punch.punch_type == PunchType.BREAK_END:
                if open_break_start is None:
                    return 0, 0, False
                break_minutes += self.__diff_in_minutes(open_break_start, punch.punched_at)
                open_break_start = None
                open_interval_start = punch.punched_at
                continue

            if punch.punch_type == PunchType.OUT:
                if open_interval_start is None or open_break_start is not None:
                    return 0, 0, False
                worked_minutes += self.__diff_in_minutes(open_interval_start, punch.punched_at)
                open_interval_start = None

        is_complete = open_interval_start is None and open_break_start is None
        return worked_minutes, break_minutes, is_complete

    def __diff_in_minutes(self, start: datetime, end: datetime) -> int:
        if end < start:
            return 0
        return int((end - start).total_seconds() // 60)
