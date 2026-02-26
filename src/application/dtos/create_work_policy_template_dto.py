from dataclasses import dataclass


@dataclass
class CreateWorkPolicyTemplateDTO:
    tenant_id: int
    name: str
    daily_work_minutes: int
    break_minutes: int
