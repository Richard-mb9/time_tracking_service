from datetime import date

from .enums import DailyAttendanceStatus


class DailyAttendanceSummary:
    id: int
    tenant_id: int
    employee_id: int
    matricula: str
    work_date: date
    expected_minutes: int
    worked_minutes: int
    break_minutes: int
    overtime_minutes: int
    deficit_minutes: int
    status: DailyAttendanceStatus

    def __init__(
        self,
        tenant_id: int,
        employee_id: int,
        matricula: str,
        work_date: date,
        expected_minutes: int,
        worked_minutes: int,
        break_minutes: int,
        overtime_minutes: int,
        deficit_minutes: int,
        status: DailyAttendanceStatus,
    ):
        self.tenant_id = tenant_id
        self.employee_id = employee_id
        self.matricula = matricula
        self.work_date = work_date
        self.expected_minutes = expected_minutes
        self.worked_minutes = worked_minutes
        self.break_minutes = break_minutes
        self.overtime_minutes = overtime_minutes
        self.deficit_minutes = deficit_minutes
        self.status = status
