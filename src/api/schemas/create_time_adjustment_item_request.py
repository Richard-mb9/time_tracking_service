from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .enums import PunchTypeRequestEnum


class CreateTimeAdjustmentItemRequest(BaseModel):
    proposedPunchType: Optional[PunchTypeRequestEnum] = None
    proposedPunchedAt: Optional[datetime] = None
    originalPunchId: Optional[int] = None
    note: Optional[str] = None
