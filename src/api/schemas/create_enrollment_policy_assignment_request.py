from datetime import date
from typing import Optional

from pydantic import BaseModel


class CreateEnrollmentPolicyAssignmentRequest(BaseModel):
    tenantId: int
    employeeId: int
    matricula: str
    templateId: int
    effectiveFrom: date
    effectiveTo: Optional[date] = None
