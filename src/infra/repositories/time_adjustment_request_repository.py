from datetime import date
from typing import Any, Dict, Optional

from application.repositories import TimeAdjustmentRequestRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import TimeAdjustmentRequest
from domain.enums import PunchType, TimeAdjustmentStatus, TimeAdjustmentType
from infra.database_manager import DatabaseManagerConnection


class TimeAdjustmentRequestRepository(TimeAdjustmentRequestRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(self, request: TimeAdjustmentRequest) -> TimeAdjustmentRequest:
        self.session.add(request)
        self.session.commit()
        self.session.refresh(request)
        return self.__normalize_request(request)

    def update(
        self, request_id: int, data: Dict[str, Any]
    ) -> Optional[TimeAdjustmentRequest]:
        request = self.find_by_id(request_id)
        if request is None:
            return None

        for key, value in data.items():
            setattr(request, key, value)

        self.session.commit()
        self.session.refresh(request)
        return self.__normalize_request(request)

    def delete(self, request_id: int) -> None:
        request = self.find_by_id(request_id)
        if request is None:
            return
        self.session.delete(request)
        self.session.commit()

    def find_by_id(self, request_id: int) -> Optional[TimeAdjustmentRequest]:
        request = (
            self.session.query(TimeAdjustmentRequest)
            .filter(TimeAdjustmentRequest.id == request_id)
            .first()
        )
        return self.__normalize_request(request) if request is not None else None

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        enrollment_id: Optional[int] = None,
        status: Optional[TimeAdjustmentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DBPaginatedResult[TimeAdjustmentRequest]:
        query = self.session.query(TimeAdjustmentRequest)

        if tenant_id is not None:
            query = query.filter(TimeAdjustmentRequest.tenant_id == tenant_id)

        if enrollment_id is not None:
            query = query.filter(TimeAdjustmentRequest.enrollment_id == enrollment_id)

        if status is not None:
            query = query.filter(TimeAdjustmentRequest.status == status)

        if start_date is not None:
            query = query.filter(TimeAdjustmentRequest.request_date >= start_date)

        if end_date is not None:
            query = query.filter(TimeAdjustmentRequest.request_date <= end_date)

        total = query.count()
        data = (
            query.order_by(TimeAdjustmentRequest.id.desc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(
            data=[self.__normalize_request(request) for request in data],
            total_count=total,
        )

    def __normalize_request(
        self, request: TimeAdjustmentRequest
    ) -> TimeAdjustmentRequest:
        if isinstance(request.request_type, str):
            request.request_type = TimeAdjustmentType(request.request_type)
        if isinstance(request.status, str):
            request.status = TimeAdjustmentStatus(request.status)
        for item in (request.items or []):
            if isinstance(item.proposed_punch_type, str):
                item.proposed_punch_type = PunchType(item.proposed_punch_type)
        return request
