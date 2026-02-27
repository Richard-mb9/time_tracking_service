from typing import Optional
from typing import List

from pydantic import BaseModel

from .work_day_policy_request import WorkDayPolicyRequest


class UpdateWorkPolicyTemplateRequest(BaseModel):
    name: Optional[str] = None
    workDayPolicies: Optional[List[WorkDayPolicyRequest]] = None
