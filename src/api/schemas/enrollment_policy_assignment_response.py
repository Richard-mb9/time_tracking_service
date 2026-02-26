from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class EnrollmentPolicyAssignmentResponse:
    id: int
    tenantId: int
    employeeId: int
    matricula: str
    templateId: int
    effectiveFrom: date
    effectiveTo: Optional[date]
