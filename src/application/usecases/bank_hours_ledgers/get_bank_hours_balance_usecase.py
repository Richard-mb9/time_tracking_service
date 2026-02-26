from application.dtos import GetBankHoursBalanceDTO
from application.repositories import RepositoryManagerInterface


class GetBankHoursBalanceUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.bank_hours_ledger_repository = repository_manager.bank_hours_ledger_repository()

    def execute(self, data: GetBankHoursBalanceDTO) -> int:
        return self.bank_hours_ledger_repository.get_balance_until(
            employee_id=data.employee_id,
            matricula=data.matricula,
            until_date=data.until_date,
        )
