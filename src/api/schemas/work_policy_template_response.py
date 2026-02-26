from dataclasses import dataclass


@dataclass
class WorkPolicyTemplateResponse:
    id: int
    tenantId: int
    name: str
    dailyWorkMinutes: int
    breakMinutes: int
