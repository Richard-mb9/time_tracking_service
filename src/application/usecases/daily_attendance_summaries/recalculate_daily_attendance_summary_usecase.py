from datetime import date, datetime
from typing import List, Optional, Tuple

from application.dtos import RecalculateDailyAttendanceSummaryDTO
from application.repositories import RepositoryManagerInterface
from application.usecases.enrollment_policy_assignments import (
    FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase,
)
from domain import (
    BankHoursLedger,
    DailyAttendanceSummary,
    EnrollmentPolicyAssignment,
    TimePunch,
    WorkWeekDay,
)
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
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()
        self.employee_holiday_calendar_assignment_repository = (
            repository_manager.employee_holiday_calendar_assignment_repository()
        )
        self.find_assignment_by_date = (
            FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase(repository_manager)
        )

    def execute(self, data: RecalculateDailyAttendanceSummaryDTO) -> DailyAttendanceSummary:
        assignment = self.find_assignment_by_date.execute(
            employee_id=data.employee_id,
            matricula=data.matricula,
            reference_date=data.work_date,
        )

        punches = self.time_punch_repository.find_by_employee_and_matricula_and_date(
            employee_id=data.employee_id,
            matricula=data.matricula,
            work_date=data.work_date,
        )
        worked_minutes, break_minutes, is_complete = self.__calculate_minutes(punches)

        expected_minutes = self.__resolve_expected_minutes(
            assignment=assignment,
            work_date=data.work_date,
        )
        is_holiday = self.__is_holiday_for_employee(
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=data.matricula,
            work_date=data.work_date,
        )
        if is_holiday:
            expected_minutes = 0

        has_pending_adjustment = self.__has_pending_adjustment(
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=data.matricula,
            work_date=data.work_date,
        )
        status = self.__resolve_status(
            assignment_exists=assignment is not None,
            has_pending_adjustment=has_pending_adjustment,
            is_complete=is_complete,
            punches_count=len(punches),
            expected_minutes=expected_minutes,
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
            employee_id=data.employee_id,
            matricula=data.matricula,
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
            employee_id=data.employee_id,
            matricula=data.matricula,
            event_date=data.work_date,
            source=BankHoursSource.DAILY_APURATION,
        )

        daily_delta = overtime_minutes - deficit_minutes
        if status == DailyAttendanceStatus.OK and daily_delta != 0:
            self.bank_hours_ledger_repository.create(
                BankHoursLedger(
                    tenant_id=data.tenant_id,
                    employee_id=data.employee_id,
                    matricula=data.matricula,
                    event_date=data.work_date,
                    minutes_delta=daily_delta,
                    source=BankHoursSource.DAILY_APURATION,
                    reference_id=persisted_summary.id,
                )
            )

        return persisted_summary

    def __has_pending_adjustment(
        self, tenant_id: int, employee_id: int, matricula: str, work_date: date
    ) -> bool:
        result = self.time_adjustment_request_repository.find_all(
            page=0,
            per_page=1,
            tenant_id=tenant_id,
            employee_id=employee_id,
            matricula=matricula,
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
        expected_minutes: int,
    ) -> DailyAttendanceStatus:
        if not assignment_exists:
            return DailyAttendanceStatus.NO_POLICY
        if has_pending_adjustment:
            return DailyAttendanceStatus.PENDING_ADJUSTMENT
        if punches_count == 0 and expected_minutes == 0:
            return DailyAttendanceStatus.OK
        if punches_count == 0:
            return DailyAttendanceStatus.INCOMPLETE
        if not is_complete:
            return DailyAttendanceStatus.INCOMPLETE
        return DailyAttendanceStatus.OK

    def __resolve_expected_minutes(
        self,
        assignment: Optional[EnrollmentPolicyAssignment],
        work_date: date,
    ) -> int:
        if assignment is None:
            return 0
        if assignment.template is None:
            return 0
        week_day = self.__to_week_day(work_date)
        policy = assignment.template.find_work_day_policy(week_day)
        if policy is None:
            return 0
        return policy.daily_work_minutes

    def __to_week_day(self, work_date: date) -> WorkWeekDay:
        day_index = work_date.weekday()
        mapping = {
            0: WorkWeekDay.MONDAY,
            1: WorkWeekDay.TUESDAY,
            2: WorkWeekDay.WEDNESDAY,
            3: WorkWeekDay.THURSDAY,
            4: WorkWeekDay.FRIDAY,
            5: WorkWeekDay.SATURDAY,
            6: WorkWeekDay.SUNDAY,
        }
        return mapping[day_index]

    def __is_holiday_for_employee(
        self, tenant_id: int, employee_id: int, matricula: str, work_date: date
    ) -> bool:
        employee_calendar_assignment = (
            self.employee_holiday_calendar_assignment_repository.find_by_employee_id_and_matricula_and_tenant_id(
                employee_id=employee_id,
                matricula=matricula,
                tenant_id=tenant_id,
            )
        )
        if employee_calendar_assignment is None:
            return False

        return self.holiday_calendar_repository.has_holiday_on_date(
            holiday_calendar_id=employee_calendar_assignment.holiday_calendar_id,
            holiday_date=work_date,
        )

    def __calculate_minutes(self, punches: List[TimePunch]) -> Tuple[int, int, bool]:
        ordered = sorted(punches, key=lambda punch: punch.punched_at)

        worked_minutes = 0
        break_minutes = 0

        open_interval_start: Optional[datetime] = None
        last_out_at: Optional[datetime] = None

        for punch in ordered:
            punch_type = (
                PunchType(punch.punch_type)
                if isinstance(punch.punch_type, str)
                else punch.punch_type
            )

            if punch_type not in [PunchType.IN, PunchType.OUT]:
                return 0, 0, False

            if punch_type == PunchType.IN:
                if open_interval_start is not None:
                    return 0, 0, False
                if last_out_at is not None:
                    break_minutes += self.__diff_in_minutes(last_out_at, punch.punched_at)
                open_interval_start = punch.punched_at
                last_out_at = None
                continue

            if punch_type == PunchType.OUT:
                if open_interval_start is None:
                    return 0, 0, False
                worked_minutes += self.__diff_in_minutes(open_interval_start, punch.punched_at)
                open_interval_start = None
                last_out_at = punch.punched_at

        is_complete = open_interval_start is None
        return worked_minutes, break_minutes, is_complete

    def __diff_in_minutes(self, start: datetime, end: datetime) -> int:
        if end < start:
            return 0
        return int((end - start).total_seconds() // 60)
