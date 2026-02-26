from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ListEnrollmentPolicyAssignmentsDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    employee_id: Optional[int] = None
    matricula: Optional[str] = None
    template_id: Optional[int] = None
    target_date: Optional[date] = None
