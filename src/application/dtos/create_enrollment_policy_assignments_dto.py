from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class CreateEnrollmentPolicyAssignmentsItemDTO:
    employee_id: int
    matricula: str


@dataclass
class CreateEnrollmentPolicyAssignmentsDTO:
    tenant_id: int
    template_id: int
    effective_from: date
    employees: List[CreateEnrollmentPolicyAssignmentsItemDTO]
    effective_to: Optional[date] = None
