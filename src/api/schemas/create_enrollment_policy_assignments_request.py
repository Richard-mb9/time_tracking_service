from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class CreateEnrollmentPolicyAssignmentsItemRequest(BaseModel):
    employeeId: int
    matricula: str


class CreateEnrollmentPolicyAssignmentsRequest(BaseModel):
    tenantId: int
    templateId: int
    effectiveFrom: date
    effectiveTo: Optional[date] = None
    employees: List[CreateEnrollmentPolicyAssignmentsItemRequest]
