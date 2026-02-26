from dataclasses import dataclass
from typing import Optional


@dataclass
class ListEmployeeEnrollmentsDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    employee_id: Optional[int] = None
    enrollment_code: Optional[str] = None
    is_active: Optional[bool] = None
