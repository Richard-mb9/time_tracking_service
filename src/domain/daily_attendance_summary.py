from datetime import date
from typing import TYPE_CHECKING

from .enums import DailyAttendanceStatus

if TYPE_CHECKING:  # pragma: no cover
    from .employee_enrollment import EmployeeEnrollment


class DailyAttendanceSummary:
    id: int
    tenant_id: int
    enrollment_id: int
    work_date: date
    expected_minutes: int
    worked_minutes: int
    break_minutes: int
    overtime_minutes: int
    deficit_minutes: int
    status: DailyAttendanceStatus

    enrollment: "EmployeeEnrollment"

    def __init__(
        self,
        tenant_id: int,
        enrollment_id: int,
        work_date: date,
        expected_minutes: int,
        worked_minutes: int,
        break_minutes: int,
        overtime_minutes: int,
        deficit_minutes: int,
        status: DailyAttendanceStatus,
    ):
        self.tenant_id = tenant_id
        self.enrollment_id = enrollment_id
        self.work_date = work_date
        self.expected_minutes = expected_minutes
        self.worked_minutes = worked_minutes
        self.break_minutes = break_minutes
        self.overtime_minutes = overtime_minutes
        self.deficit_minutes = deficit_minutes
        self.status = status
