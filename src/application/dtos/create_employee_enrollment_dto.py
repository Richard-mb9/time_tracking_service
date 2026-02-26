from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CreateEmployeeEnrollmentDTO:
    tenant_id: int
    employee_id: int
    enrollment_code: str
    active_from: date
    active_to: Optional[date] = None
    is_active: bool = True
