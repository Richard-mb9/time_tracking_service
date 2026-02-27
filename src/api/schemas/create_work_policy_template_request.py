from typing import List

from pydantic import BaseModel

from .work_day_policy_request import WorkDayPolicyRequest


class CreateWorkPolicyTemplateRequest(BaseModel):
    tenantId: int
    name: str
    workDayPolicies: List[WorkDayPolicyRequest]
