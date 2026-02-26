from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import BankHoursLedger


class FindBankHoursLedgerEntryByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.bank_hours_ledger_repository = repository_manager.bank_hours_ledger_repository()

    @overload
    def execute(self, entry_id: int) -> Optional[BankHoursLedger]:
        pass

    @overload
    def execute(self, entry_id: int, raise_if_is_none: Literal[True]) -> BankHoursLedger:
        pass

    @overload
    def execute(
        self, entry_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[BankHoursLedger]:
        pass

    def execute(self, entry_id: int, raise_if_is_none: bool = False):
        entry = self.bank_hours_ledger_repository.find_by_id(entry_id)
        if raise_if_is_none and entry is None:
            raise NotFoundError("Bank hours ledger entry not found.")
        return entry
