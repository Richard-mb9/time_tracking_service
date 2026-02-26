from pydantic import BaseModel


class CreateWorkPolicyTemplateRequest(BaseModel):
    tenantId: int
    name: str
    dailyWorkMinutes: int
    breakMinutes: int
