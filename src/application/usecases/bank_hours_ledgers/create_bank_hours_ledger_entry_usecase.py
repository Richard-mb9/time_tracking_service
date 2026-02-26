from application.dtos import CreateBankHoursLedgerEntryDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from domain import BankHoursLedger


class CreateBankHoursLedgerEntryUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.bank_hours_ledger_repository = repository_manager.bank_hours_ledger_repository()

    def execute(self, data: CreateBankHoursLedgerEntryDTO) -> BankHoursLedger:
        matricula = data.matricula.strip()
        if len(matricula) == 0:
            raise BadRequestError("matricula is required.")

        if data.minutes_delta == 0:
            raise BadRequestError("minutes_delta cannot be zero.")

        entry = BankHoursLedger(
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=matricula,
            event_date=data.event_date,
            minutes_delta=data.minutes_delta,
            source=data.source,
            reference_id=data.reference_id,
        )
        return self.bank_hours_ledger_repository.create(entry)
