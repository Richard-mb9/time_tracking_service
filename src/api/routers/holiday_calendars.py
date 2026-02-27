from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import HolidayCalendarsController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    AssignEmployeeHolidayCalendarRequest,
    CreateHolidayCalendarRequest,
    DefaultCreateResponse,
    DefaultResponse,
    EmployeeHolidayCalendarAssignmentResponse,
    HolidayCalendarResponse,
    PaginatedResponse,
    UfRequestEnum,
    UpdateHolidayCalendarRequest,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("holiday_calendars:create")],
)
async def create_holiday_calendar(
    data: CreateHolidayCalendarRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return HolidayCalendarsController(db_manager).create(data)


@router.get(
    "/{holidayCalendarId}",
    status_code=HTTPStatus.OK,
    response_model=HolidayCalendarResponse,
    dependencies=[require_role("holiday_calendars:read")],
)
async def get_holiday_calendar(
    holidayCalendarId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return HolidayCalendarsController(db_manager).find_by_id(
        holiday_calendar_id=holidayCalendarId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[HolidayCalendarResponse],
    dependencies=[require_role("holiday_calendars:read")],
)
async def list_holiday_calendars(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=1000),
    name: Optional[str] = None,
    city: Optional[str] = None,
    uf: Optional[UfRequestEnum] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return HolidayCalendarsController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        name=name,
        city=city,
        uf=uf.value if uf is not None else None,
    )


@router.put(
    "/{holidayCalendarId}",
    status_code=HTTPStatus.OK,
    response_model=HolidayCalendarResponse,
    dependencies=[require_role("holiday_calendars:edit")],
)
async def update_holiday_calendar(
    holidayCalendarId: int,
    data: UpdateHolidayCalendarRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return HolidayCalendarsController(db_manager).update(
        holiday_calendar_id=holidayCalendarId,
        tenant_id=current_user.tenant_id,
        data=data,
    )


@router.delete(
    "/{holidayCalendarId}",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("holiday_calendars:delete")],
)
async def delete_holiday_calendar(
    holidayCalendarId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    HolidayCalendarsController(db_manager).delete(
        holiday_calendar_id=holidayCalendarId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(message="Holiday calendar deleted successfully")


@router.get(
    "/employees/{employeeId}/assignment",
    status_code=HTTPStatus.OK,
    response_model=EmployeeHolidayCalendarAssignmentResponse,
    dependencies=[require_role("holiday_calendars:read")],
)
async def find_employee_holiday_calendar_assignment(
    employeeId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return HolidayCalendarsController(
        db_manager
    ).find_employee_holiday_calendar_assignment(
        employee_id=employeeId,
        tenant_id=current_user.tenant_id,
    )


@router.put(
    "/employees/{employeeId}/assignment",
    status_code=HTTPStatus.OK,
    response_model=EmployeeHolidayCalendarAssignmentResponse,
    dependencies=[require_role("holiday_calendars:edit")],
)
async def assign_employee_holiday_calendar(
    employeeId: int,
    data: AssignEmployeeHolidayCalendarRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return HolidayCalendarsController(db_manager).assign_employee_holiday_calendar(
        employee_id=employeeId,
        tenant_id=current_user.tenant_id,
        data=data,
    )


@router.delete(
    "/employees/{employeeId}/assignment",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("holiday_calendars:delete")],
)
async def remove_employee_holiday_calendar_assignment(
    employeeId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    HolidayCalendarsController(db_manager).remove_employee_holiday_calendar_assignment(
        employee_id=employeeId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(
        message="Employee holiday calendar assignment removed successfully"
    )
