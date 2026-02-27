from dataclasses import dataclass
from typing import List, Optional

from .work_day_policy_dto import WorkDayPolicyDTO


@dataclass
class UpdateWorkPolicyTemplateDTO:
    name: Optional[str] = None
    work_day_policies: Optional[List[WorkDayPolicyDTO]] = None
