from datetime import date
from typing import Optional

from pydantic import BaseModel


class CreateEmployeeEnrollmentRequest(BaseModel):
    tenantId: int
    employeeId: int
    enrollmentCode: str
    activeFrom: date
    activeTo: Optional[date] = None
    isActive: bool = True
