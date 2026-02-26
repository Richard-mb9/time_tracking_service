from dataclasses import dataclass
from typing import Optional


@dataclass
class ListWorkPolicyTemplatesDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    name: Optional[str] = None
