from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AccessTokenData:
    session_id: int
    user_id: int
    roles: List[str]
    username: str
    validated: bool
    tenant_id: int
    email: Optional[str]
