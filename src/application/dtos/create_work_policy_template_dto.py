from dataclasses import dataclass
from typing import List

from .work_day_policy_dto import WorkDayPolicyDTO


@dataclass
class CreateWorkPolicyTemplateDTO:
    tenant_id: int
    name: str
    work_day_policies: List[WorkDayPolicyDTO]
