from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import EmployeeEnrollmentsController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    CreateEmployeeEnrollmentRequest,
    DefaultCreateResponse,
    DefaultResponse,
    EmployeeEnrollmentResponse,
    PaginatedResponse,
    UpdateEmployeeEnrollmentRequest,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("employee_enrollments:create")],
)
async def create_employee_enrollment(
    data: CreateEmployeeEnrollmentRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return EmployeeEnrollmentsController(db_manager).create(data)


@router.get(
    "/{enrollmentId}",
    status_code=HTTPStatus.OK,
    response_model=EmployeeEnrollmentResponse,
    dependencies=[require_role("employee_enrollments:read")],
)
async def get_employee_enrollment(
    enrollmentId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return EmployeeEnrollmentsController(db_manager).find_by_id(
        enrollment_id=enrollmentId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[EmployeeEnrollmentResponse],
    dependencies=[require_role("employee_enrollments:read")],
)
async def list_employee_enrollments(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
    employeeId: Optional[int] = None,
    enrollmentCode: Optional[str] = None,
    isActive: Optional[bool] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return EmployeeEnrollmentsController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        employee_id=employeeId,
        enrollment_code=enrollmentCode,
        is_active=isActive,
    )


@router.put(
    "/{enrollmentId}",
    status_code=HTTPStatus.OK,
    response_model=EmployeeEnrollmentResponse,
    dependencies=[require_role("employee_enrollments:edit")],
)
async def update_employee_enrollment(
    enrollmentId: int,
    data: UpdateEmployeeEnrollmentRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return EmployeeEnrollmentsController(db_manager).update(
        enrollment_id=enrollmentId,
        tenant_id=current_user.tenant_id,
        data=data,
    )


@router.delete(
    "/{enrollmentId}",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("employee_enrollments:write")],
)
async def delete_employee_enrollment(
    enrollmentId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    EmployeeEnrollmentsController(db_manager).delete(
        enrollment_id=enrollmentId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(message="Employee enrollment deleted successfully")
