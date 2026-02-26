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
        self,
        employee_id: int,
        matricula: str,
        punched_at: datetime,
        punch_type: PunchType,
    ) -> Optional[TimePunch]:
        punch = (
            self.session.query(TimePunch)
            .filter(TimePunch.employee_id == employee_id)
            .filter(TimePunch.matricula == matricula)
            .filter(TimePunch.punched_at == punched_at)
            .filter(TimePunch.punch_type == punch_type)
            .first()
        )
        return self.__normalize_punch(punch) if punch is not None else None

    def find_last_by_employee_and_matricula(
        self, employee_id: int, matricula: str
    ) -> Optional[TimePunch]:
        punch = (
            self.session.query(TimePunch)
            .filter(TimePunch.employee_id == employee_id)
            .filter(TimePunch.matricula == matricula)
            .order_by(TimePunch.punched_at.desc())
            .first()
        )
        return self.__normalize_punch(punch) if punch is not None else None

    def find_by_employee_and_matricula_and_period(
        self, employee_id: int, matricula: str, start_at: datetime, end_at: datetime
    ) -> List[TimePunch]:
        data = (
            self.session.query(TimePunch)
            .filter(TimePunch.employee_id == employee_id)
            .filter(TimePunch.matricula == matricula)
            .filter(TimePunch.punched_at >= start_at)
            .filter(TimePunch.punched_at <= end_at)
            .order_by(TimePunch.punched_at.asc())
            .all()
        )
        return [self.__normalize_punch(punch) for punch in data]

    def find_by_employee_and_matricula_and_date(
        self, employee_id: int, matricula: str, work_date: date
    ) -> List[TimePunch]:
        data = (
            self.session.query(TimePunch)
            .filter(TimePunch.employee_id == employee_id)
            .filter(TimePunch.matricula == matricula)
            .filter(func.date(TimePunch.punched_at) == work_date)
            .order_by(TimePunch.punched_at.asc())
            .all()
        )
        return [self.__normalize_punch(punch) for punch in data]

    def find_other_matriculas_with_punch_on_date(
        self,
        tenant_id: int,
        employee_id: int,
        work_date: date,
        matricula_to_exclude: str,
    ) -> List[TimePunch]:
        data = (
            self.session.query(TimePunch)
            .filter(TimePunch.tenant_id == tenant_id)
            .filter(TimePunch.employee_id == employee_id)
            .filter(TimePunch.matricula != matricula_to_exclude)
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
        employee_id: Optional[int] = None,
        matricula: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        punch_type: Optional[PunchType] = None,
    ) -> DBPaginatedResult[TimePunch]:
        query = self.session.query(TimePunch)

        if tenant_id is not None:
            query = query.filter(TimePunch.tenant_id == tenant_id)

        if employee_id is not None:
            query = query.filter(TimePunch.employee_id == employee_id)

        if matricula is not None:
            query = query.filter(TimePunch.matricula == matricula)

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
