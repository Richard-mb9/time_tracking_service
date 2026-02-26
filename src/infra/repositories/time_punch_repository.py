from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func

from application.repositories import TimePunchRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import TimePunch
from domain.enums import PunchType
from infra.database_manager import DatabaseManagerConnection


class TimePunchRepository(TimePunchRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(self, punch: TimePunch) -> TimePunch:
        self.session.add(punch)
        self.session.commit()
        self.session.refresh(punch)
        return self.__normalize_punch(punch)

    def update(self, punch_id: int, data: Dict[str, Any]) -> Optional[TimePunch]:
        punch = self.find_by_id(punch_id)
        if punch is None:
            return None

        for key, value in data.items():
            setattr(punch, key, value)

        self.session.commit()
        self.session.refresh(punch)
        return self.__normalize_punch(punch)

    def delete(self, punch_id: int) -> None:
        punch = self.find_by_id(punch_id)
        if punch is None:
            return
        self.session.delete(punch)
        self.session.commit()

    def find_by_id(self, punch_id: int) -> Optional[TimePunch]:
        punch = self.session.query(TimePunch).filter(TimePunch.id == punch_id).first()
        return self.__normalize_punch(punch) if punch is not None else None

    def find_duplicate(
        self, enrollment_id: int, punched_at: datetime, punch_type: PunchType
    ) -> Optional[TimePunch]:
        punch = (
            self.session.query(TimePunch)
            .filter(TimePunch.enrollment_id == enrollment_id)
            .filter(TimePunch.punched_at == punched_at)
            .filter(TimePunch.punch_type == punch_type)
            .first()
        )
        return self.__normalize_punch(punch) if punch is not None else None

    def find_last_by_enrollment(self, enrollment_id: int) -> Optional[TimePunch]:
        punch = (
            self.session.query(TimePunch)
            .filter(TimePunch.enrollment_id == enrollment_id)
            .order_by(TimePunch.punched_at.desc())
            .first()
        )
        return self.__normalize_punch(punch) if punch is not None else None

    def find_by_enrollment_and_period(
        self, enrollment_id: int, start_at: datetime, end_at: datetime
    ) -> List[TimePunch]:
        data = (
            self.session.query(TimePunch)
            .filter(TimePunch.enrollment_id == enrollment_id)
            .filter(TimePunch.punched_at >= start_at)
            .filter(TimePunch.punched_at <= end_at)
            .order_by(TimePunch.punched_at.asc())
            .all()
        )
        return [self.__normalize_punch(punch) for punch in data]

    def find_by_enrollment_and_date(
        self, enrollment_id: int, work_date: date
    ) -> List[TimePunch]:
        data = (
            self.session.query(TimePunch)
            .filter(TimePunch.enrollment_id == enrollment_id)
            .filter(func.date(TimePunch.punched_at) == work_date)
            .order_by(TimePunch.punched_at.asc())
            .all()
        )
        return [self.__normalize_punch(punch) for punch in data]

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        enrollment_id: Optional[int] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        punch_type: Optional[PunchType] = None,
    ) -> DBPaginatedResult[TimePunch]:
        query = self.session.query(TimePunch)

        if tenant_id is not None:
            query = query.filter(TimePunch.tenant_id == tenant_id)

        if enrollment_id is not None:
            query = query.filter(TimePunch.enrollment_id == enrollment_id)

        if start_at is not None:
            query = query.filter(TimePunch.punched_at >= start_at)

        if end_at is not None:
            query = query.filter(TimePunch.punched_at <= end_at)

        if punch_type is not None:
            query = query.filter(TimePunch.punch_type == punch_type)

        total = query.count()
        data = (
            query.order_by(TimePunch.punched_at.desc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(
            data=[self.__normalize_punch(punch) for punch in data],
            total_count=total,
        )

    def __normalize_punch(self, punch: TimePunch) -> TimePunch:
        if isinstance(punch.punch_type, str):
            punch.punch_type = PunchType(punch.punch_type)
        return punch
