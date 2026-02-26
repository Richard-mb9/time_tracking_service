from typing import Optional

from pydantic import BaseModel


class UpdateWorkPolicyTemplateRequest(BaseModel):
    name: Optional[str] = None
    dailyWorkMinutes: Optional[int] = None
    breakMinutes: Optional[int] = None
