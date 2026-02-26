from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CreateEnrollmentPolicyAssignmentDTO:
    tenant_id: int
    enrollment_id: int
    template_id: int
    effective_from: date
    effective_to: Optional[date] = None
