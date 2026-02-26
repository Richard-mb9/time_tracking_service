from datetime import date
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import BankHoursLedgersController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    BankHoursSourceRequestEnum,
    BankHoursBalanceResponse,
    BankHoursLedgerResponse,
    CreateBankHoursLedgerEntryRequest,
    DefaultCreateResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("bank_hours_ledgers:create")],
)
async def create_bank_hours_ledger_entry(
    data: CreateBankHoursLedgerEntryRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return BankHoursLedgersController(db_manager).create(data)


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[BankHoursLedgerResponse],
    dependencies=[require_role("bank_hours_ledgers:read")],
)
async def list_bank_hours_ledger_entries(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=1000),
    employeeId: Optional[int] = None,
    matricula: Optional[str] = None,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    source: Optional[BankHoursSourceRequestEnum] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return BankHoursLedgersController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        employee_id=employeeId,
        matricula=matricula,
        start_date=startDate,
        end_date=endDate,
        source=source,
    )


@router.get(
    "/balance",
    status_code=HTTPStatus.OK,
    response_model=BankHoursBalanceResponse,
    dependencies=[require_role("bank_hours_ledgers:read")],
)
async def get_bank_hours_balance(
    employeeId: int,
    matricula: str,
    untilDate: date,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return BankHoursLedgersController(db_manager).get_balance(
        employee_id=employeeId,
        matricula=matricula,
        until_date=untilDate,
    )


@router.get(
    "/{entryId}",
    status_code=HTTPStatus.OK,
    response_model=BankHoursLedgerResponse,
    dependencies=[require_role("bank_hours_ledgers:read")],
)
async def get_bank_hours_ledger_entry(
    entryId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return BankHoursLedgersController(db_manager).find_by_id(
        entry_id=entryId,
        tenant_id=current_user.tenant_id,
    )
