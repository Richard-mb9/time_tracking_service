from datetime import datetime
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import TimePunchesController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    CreateTimePunchRequest,
    DefaultCreateResponse,
    DefaultResponse,
    PaginatedResponse,
    PunchTypeRequestEnum,
    TimePunchResponse,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("time_punches:create")],
)
async def create_time_punch(
    data: CreateTimePunchRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return TimePunchesController(db_manager).create(data)


@router.get(
    "/{punchId}",
    status_code=HTTPStatus.OK,
    response_model=TimePunchResponse,
    dependencies=[require_role("time_punches:read")],
)
async def get_time_punch(
    punchId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return TimePunchesController(db_manager).find_by_id(
        punch_id=punchId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[TimePunchResponse],
    dependencies=[require_role("time_punches:read")],
)
async def list_time_punches(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=1000),
    employeeId: Optional[int] = None,
    matricula: Optional[str] = None,
    startAt: Optional[datetime] = None,
    endAt: Optional[datetime] = None,
    punchType: Optional[PunchTypeRequestEnum] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return TimePunchesController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        employee_id=employeeId,
        matricula=matricula,
        start_at=startAt,
        end_at=endAt,
        punch_type=punchType,
    )


@router.delete(
    "/{punchId}",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("time_punches:write")],
)
async def delete_time_punch(
    punchId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    TimePunchesController(db_manager).delete(
        punch_id=punchId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(message="Time punch deleted successfully")
