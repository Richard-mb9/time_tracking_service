from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateWorkPolicyTemplateDTO:
    name: Optional[str] = None
    daily_work_minutes: Optional[int] = None
    break_minutes: Optional[int] = None
