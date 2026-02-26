from dataclasses import dataclass
from datetime import date


@dataclass
class DailyAttendanceSummaryResponse:
    id: int
    tenantId: int
    employeeId: int
    matricula: str
    workDate: date
    expectedMinutes: int
    workedMinutes: int
    breakMinutes: int
    overtimeMinutes: int
    deficitMinutes: int
    status: str
