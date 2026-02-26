from datetime import date
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import DailyAttendanceSummariesController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    DailyAttendanceSummaryResponse,
    DailyAttendanceStatusRequestEnum,
    PaginatedResponse,
    RecalculateDailyAttendanceSummaryRequest,
)

router = APIRouter()


@router.post(
    "/recalculate",
    status_code=HTTPStatus.OK,
    response_model=DailyAttendanceSummaryResponse,
    dependencies=[require_role("daily_attendance_summaries:edit")],
)
async def recalculate_daily_attendance_summary(
    data: RecalculateDailyAttendanceSummaryRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return DailyAttendanceSummariesController(db_manager).recalculate(data)


@router.get(
    "/{summaryId}",
    status_code=HTTPStatus.OK,
    response_model=DailyAttendanceSummaryResponse,
    dependencies=[require_role("daily_attendance_summaries:read")],
)
async def get_daily_attendance_summary(
    summaryId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return DailyAttendanceSummariesController(db_manager).find_by_id(
        summary_id=summaryId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[DailyAttendanceSummaryResponse],
    dependencies=[require_role("daily_attendance_summaries:read")],
)
async def list_daily_attendance_summaries(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
    enrollmentId: Optional[int] = None,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    status: Optional[DailyAttendanceStatusRequestEnum] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return DailyAttendanceSummariesController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        enrollment_id=enrollmentId,
        start_date=startDate,
        end_date=endDate,
        status=status,
    )
