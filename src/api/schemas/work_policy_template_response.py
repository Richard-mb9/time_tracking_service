from dataclasses import dataclass, field
from typing import List


@dataclass
class WorkDayPolicyResponse:
    id: int
    weekDay: str
    dailyWorkMinutes: int
    breakMinutes: int


@dataclass
class WorkPolicyTemplateResponse:
    id: int
    tenantId: int
    name: str
    workDayPolicies: List[WorkDayPolicyResponse] = field(default_factory=list)
