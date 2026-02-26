from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, Optional

from application.repositories.types import DBPaginatedResult
from domain import TimeAdjustmentRequest
from domain.enums import TimeAdjustmentStatus


class TimeAdjustmentRequestRepositoryInterface(ABC):
    @abstractmethod
    def create(self, request: TimeAdjustmentRequest) -> TimeAdjustmentRequest:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, request_id: int, data: Dict[str, Any]
    ) -> Optional[TimeAdjustmentRequest]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, request_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, request_id: int) -> Optional[TimeAdjustmentRequest]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        matricula: Optional[str] = None,
        status: Optional[TimeAdjustmentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DBPaginatedResult[TimeAdjustmentRequest]:
        raise NotImplementedError
