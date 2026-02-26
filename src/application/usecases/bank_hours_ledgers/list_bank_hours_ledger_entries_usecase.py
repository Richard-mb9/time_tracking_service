from application.dtos import ListBankHoursLedgerEntriesDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import BankHoursLedger


class ListBankHoursLedgerEntriesUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.bank_hours_ledger_repository = repository_manager.bank_hours_ledger_repository()

    def execute(self, data: ListBankHoursLedgerEntriesDTO) -> PaginatedResult[BankHoursLedger]:
        result = self.bank_hours_ledger_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=data.matricula,
            start_date=data.start_date,
            end_date=data.end_date,
            source=data.source,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
