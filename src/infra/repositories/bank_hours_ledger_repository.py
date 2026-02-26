from datetime import date
from typing import Optional

from sqlalchemy import func

from application.repositories import BankHoursLedgerRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import BankHoursLedger
from domain.enums import BankHoursSource
from infra.database_manager import DatabaseManagerConnection


class BankHoursLedgerRepository(BankHoursLedgerRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(self, entry: BankHoursLedger) -> BankHoursLedger:
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return self.__normalize_entry(entry)

    def find_by_id(self, entry_id: int) -> Optional[BankHoursLedger]:
        entry = (
            self.session.query(BankHoursLedger)
            .filter(BankHoursLedger.id == entry_id)
            .first()
        )
        return self.__normalize_entry(entry) if entry is not None else None

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        matricula: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        source: Optional[BankHoursSource] = None,
    ) -> DBPaginatedResult[BankHoursLedger]:
        query = self.session.query(BankHoursLedger)

        if tenant_id is not None:
            query = query.filter(BankHoursLedger.tenant_id == tenant_id)

        if employee_id is not None:
            query = query.filter(BankHoursLedger.employee_id == employee_id)

        if matricula is not None:
            query = query.filter(BankHoursLedger.matricula == matricula)

        if start_date is not None:
            query = query.filter(BankHoursLedger.event_date >= start_date)

        if end_date is not None:
            query = query.filter(BankHoursLedger.event_date <= end_date)

        if source is not None:
            query = query.filter(BankHoursLedger.source == source)

        total = query.count()
        data = (
            query.order_by(BankHoursLedger.event_date.desc(), BankHoursLedger.id.desc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(
            data=[self.__normalize_entry(entry) for entry in data],
            total_count=total,
        )

    def get_balance_until(self, employee_id: int, matricula: str, until_date: date) -> int:
        result = (
            self.session.query(func.coalesce(func.sum(BankHoursLedger.minutes_delta), 0))
            .filter(BankHoursLedger.employee_id == employee_id)
            .filter(BankHoursLedger.matricula == matricula)
            .filter(BankHoursLedger.event_date <= until_date)
            .scalar()
        )
        return int(result or 0)

    def delete_auto_generated_for_day(
        self, employee_id: int, matricula: str, event_date: date, source: BankHoursSource
    ) -> None:
        (
            self.session.query(BankHoursLedger)
            .filter(BankHoursLedger.employee_id == employee_id)
            .filter(BankHoursLedger.matricula == matricula)
            .filter(BankHoursLedger.event_date == event_date)
            .filter(BankHoursLedger.source == source)
            .delete(synchronize_session=False)
        )
        self.session.commit()

    def __normalize_entry(self, entry: BankHoursLedger) -> BankHoursLedger:
        if isinstance(entry.source, str):
            entry.source = BankHoursSource(entry.source)
        return entry
