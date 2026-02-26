from datetime import date
from typing import Optional

from api.schemas import (
    BankHoursSourceRequestEnum,
    BankHoursBalanceResponse,
    BankHoursLedgerResponse,
    CreateBankHoursLedgerEntryRequest,
    DefaultCreateResponse,
    PaginatedResponse,
)
from application.exceptions import BadRequestError
from application.dtos import (
    CreateBankHoursLedgerEntryDTO,
    GetBankHoursBalanceDTO,
    ListBankHoursLedgerEntriesDTO,
)
from application.usecases.bank_hours_ledgers import (
    CreateBankHoursLedgerEntryUseCase,
    FindBankHoursLedgerEntryByIdUseCase,
    GetBankHoursBalanceUseCase,
    ListBankHoursLedgerEntriesUseCase,
)
from application.usecases.employee_enrollments import FindEmployeeEnrollmentByIdUseCase
from domain import BankHoursLedger
from domain.enums import BankHoursSource
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class BankHoursLedgersController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateBankHoursLedgerEntryRequest) -> DefaultCreateResponse:
        entry = CreateBankHoursLedgerEntryUseCase(self.repository_manager).execute(
            CreateBankHoursLedgerEntryDTO(
                tenant_id=data.tenantId,
                enrollment_id=data.enrollmentId,
                event_date=data.eventDate,
                minutes_delta=data.minutesDelta,
                source=BankHoursSource(data.source.value),
                reference_id=data.referenceId,
            )
        )
        return DefaultCreateResponse(id=entry.id)

    def find_by_id(self, entry_id: int, tenant_id: int) -> BankHoursLedgerResponse:
        entry = FindBankHoursLedgerEntryByIdUseCase(self.repository_manager).execute(
            entry_id=entry_id,
            raise_if_is_none=True,
        )
        if entry.tenant_id != tenant_id:
            raise BadRequestError("Ledger entry does not belong to tenant.")
        return self.__to_response(entry)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        enrollment_id: Optional[int],
        start_date: Optional[date],
        end_date: Optional[date],
        source: Optional[BankHoursSourceRequestEnum],
    ) -> PaginatedResponse[BankHoursLedgerResponse]:
        mapped_source = BankHoursSource(source.value) if source is not None else None
        result = ListBankHoursLedgerEntriesUseCase(self.repository_manager).execute(
            ListBankHoursLedgerEntriesDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                enrollment_id=enrollment_id,
                start_date=start_date,
                end_date=end_date,
                source=mapped_source,
            )
        )
        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def get_balance(
        self, enrollment_id: int, until_date: date, tenant_id: int
    ) -> BankHoursBalanceResponse:
        enrollment = FindEmployeeEnrollmentByIdUseCase(self.repository_manager).execute(
            enrollment_id=enrollment_id,
            raise_if_is_none=True,
        )
        if enrollment.tenant_id != tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")

        balance = GetBankHoursBalanceUseCase(self.repository_manager).execute(
            GetBankHoursBalanceDTO(
                enrollment_id=enrollment_id,
                until_date=until_date,
            )
        )
        return BankHoursBalanceResponse(
            enrollmentId=enrollment_id,
            untilDate=until_date,
            balanceMinutes=balance,
        )

    def __to_response(self, item: BankHoursLedger) -> BankHoursLedgerResponse:
        return BankHoursLedgerResponse(
            id=item.id,
            tenantId=item.tenant_id,
            enrollmentId=item.enrollment_id,
            eventDate=item.event_date,
            minutesDelta=item.minutes_delta,
            source=item.source.value,
            referenceId=item.reference_id,
        )
