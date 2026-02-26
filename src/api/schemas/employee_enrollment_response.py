from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class EmployeeEnrollmentResponse:
    id: int
    tenantId: int
    employeeId: int
    enrollmentCode: str
    activeFrom: date
    activeTo: Optional[date]
    isActive: bool
