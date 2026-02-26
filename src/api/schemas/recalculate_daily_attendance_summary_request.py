from datetime import date

from pydantic import BaseModel


class RecalculateDailyAttendanceSummaryRequest(BaseModel):
    tenantId: int
    employeeId: int
    matricula: str
    workDate: date
