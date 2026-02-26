from application.dtos import CreateBankHoursLedgerEntryDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from application.usecases.employee_enrollments import FindEmployeeEnrollmentByIdUseCase
from domain import BankHoursLedger


class CreateBankHoursLedgerEntryUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.bank_hours_ledger_repository = repository_manager.bank_hours_ledger_repository()
        self.find_enrollment_by_id = FindEmployeeEnrollmentByIdUseCase(repository_manager)

    def execute(self, data: CreateBankHoursLedgerEntryDTO) -> BankHoursLedger:
        enrollment = self.find_enrollment_by_id.execute(
            enrollment_id=data.enrollment_id,
            raise_if_is_none=True,
        )
        if enrollment.tenant_id != data.tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")

        if data.minutes_delta == 0:
            raise BadRequestError("minutes_delta cannot be zero.")

        entry = BankHoursLedger(
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            event_date=data.event_date,
            minutes_delta=data.minutes_delta,
            source=data.source,
            reference_id=data.reference_id,
        )
        return self.bank_hours_ledger_repository.create(entry)
