from datetime import date

from pydantic import BaseModel


class RecalculateDailyAttendanceSummaryRequest(BaseModel):
    tenantId: int
    enrollmentId: int
    workDate: date
