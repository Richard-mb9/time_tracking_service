from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class UpdateEmployeeEnrollmentDTO:
    employee_id: Optional[int] = None
    enrollment_code: Optional[str] = None
    active_from: Optional[date] = None
    active_to: Optional[date] = None
    is_active: Optional[bool] = None
