from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.enums import DailyAttendanceStatus


@dataclass
class ListDailyAttendanceSummariesDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    employee_id: Optional[int] = None
    matricula: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[DailyAttendanceStatus] = None
