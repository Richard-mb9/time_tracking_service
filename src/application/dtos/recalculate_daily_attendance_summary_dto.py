from dataclasses import dataclass
from datetime import date


@dataclass
class RecalculateDailyAttendanceSummaryDTO:
    tenant_id: int
    employee_id: int
    matricula: str
    work_date: date
