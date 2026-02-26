from datetime import date
from typing import Optional

from pydantic import BaseModel


class UpdateEmployeeEnrollmentRequest(BaseModel):
    employeeId: Optional[int] = None
    enrollmentCode: Optional[str] = None
    activeFrom: Optional[date] = None
    activeTo: Optional[date] = None
    isActive: Optional[bool] = None
