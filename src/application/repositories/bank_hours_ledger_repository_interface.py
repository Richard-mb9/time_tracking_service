from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from application.repositories.types import DBPaginatedResult
from domain import BankHoursLedger
from domain.enums import BankHoursSource


class BankHoursLedgerRepositoryInterface(ABC):
    @abstractmethod
    def create(self, entry: BankHoursLedger) -> BankHoursLedger:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, entry_id: int) -> Optional[BankHoursLedger]:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def get_balance_until(self, employee_id: int, matricula: str, until_date: date) -> int:
        raise NotImplementedError

    @abstractmethod
    def delete_auto_generated_for_day(
        self, employee_id: int, matricula: str, event_date: date, source: BankHoursSource
    ) -> None:
        raise NotImplementedError
