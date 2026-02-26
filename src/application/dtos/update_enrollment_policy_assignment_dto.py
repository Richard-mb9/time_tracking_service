from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class UpdateEnrollmentPolicyAssignmentDTO:
    template_id: Optional[int] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
