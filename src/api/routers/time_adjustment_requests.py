from datetime import date
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import TimeAdjustmentRequestsController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    CreateTimeAdjustmentRequest,
    DecideTimeAdjustmentRequest,
    DefaultCreateResponse,
    DefaultResponse,
    PaginatedResponse,
    TimeAdjustmentRequestResponse,
    TimeAdjustmentStatusRequestEnum,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("time_adjustment_requests:create")],
)
async def create_time_adjustment_request(
    data: CreateTimeAdjustmentRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return TimeAdjustmentRequestsController(
        db_manager=db_manager,
        access_token=current_user,
    ).create(data)


@router.get(
    "/{requestId}",
    status_code=HTTPStatus.OK,
    response_model=TimeAdjustmentRequestResponse,
    dependencies=[require_role("time_adjustment_requests:read")],
)
async def get_time_adjustment_request(
    requestId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return TimeAdjustmentRequestsController(
        db_manager=db_manager,
        access_token=current_user,
    ).find_by_id(
        request_id=requestId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[TimeAdjustmentRequestResponse],
    dependencies=[require_role("time_adjustment_requests:read")],
)
async def list_time_adjustment_requests(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
    enrollmentId: Optional[int] = None,
    status: Optional[TimeAdjustmentStatusRequestEnum] = None,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return TimeAdjustmentRequestsController(
        db_manager=db_manager,
        access_token=current_user,
    ).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        enrollment_id=enrollmentId,
        status=status,
        start_date=startDate,
        end_date=endDate,
    )


@router.patch(
    "/{requestId}/decision",
    status_code=HTTPStatus.OK,
    response_model=TimeAdjustmentRequestResponse,
    dependencies=[require_role("time_adjustment_requests:edit")],
)
async def decide_time_adjustment_request(
    requestId: int,
    data: DecideTimeAdjustmentRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return TimeAdjustmentRequestsController(
        db_manager=db_manager,
        access_token=current_user,
    ).decide(
        request_id=requestId,
        tenant_id=current_user.tenant_id,
        data=data,
    )


@router.patch(
    "/{requestId}/apply",
    status_code=HTTPStatus.OK,
    response_model=TimeAdjustmentRequestResponse,
    dependencies=[require_role("time_adjustment_requests:edit")],
)
async def apply_time_adjustment_request(
    requestId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return TimeAdjustmentRequestsController(
        db_manager=db_manager,
        access_token=current_user,
    ).apply(
        request_id=requestId,
        tenant_id=current_user.tenant_id,
    )


@router.delete(
    "/{requestId}",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("time_adjustment_requests:write")],
)
async def delete_time_adjustment_request(
    requestId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    TimeAdjustmentRequestsController(
        db_manager=db_manager,
        access_token=current_user,
    ).delete(
        request_id=requestId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(message="Time adjustment request deleted successfully")
