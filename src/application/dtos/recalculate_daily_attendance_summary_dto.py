from dataclasses import dataclass
from datetime import date


@dataclass
class RecalculateDailyAttendanceSummaryDTO:
    tenant_id: int
    enrollment_id: int
    work_date: date
