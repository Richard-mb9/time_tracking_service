from datetime import date
from typing import Optional

from pydantic import BaseModel


class UpdateEnrollmentPolicyAssignmentRequest(BaseModel):
    templateId: Optional[int] = None
    effectiveFrom: Optional[date] = None
    effectiveTo: Optional[date] = None
