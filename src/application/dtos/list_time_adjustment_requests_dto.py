from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.enums import TimeAdjustmentStatus


@dataclass
class ListTimeAdjustmentRequestsDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    enrollment_id: Optional[int] = None
    status: Optional[TimeAdjustmentStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
