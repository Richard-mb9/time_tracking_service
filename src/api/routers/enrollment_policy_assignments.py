from datetime import date
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import EnrollmentPolicyAssignmentsController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    CreateEnrollmentPolicyAssignmentRequest,
    DefaultCreateResponse,
    DefaultResponse,
    EnrollmentPolicyAssignmentResponse,
    PaginatedResponse,
    UpdateEnrollmentPolicyAssignmentRequest,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("enrollment_policy_assignments:create")],
)
async def create_enrollment_policy_assignment(
    data: CreateEnrollmentPolicyAssignmentRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return EnrollmentPolicyAssignmentsController(db_manager).create(data)


@router.get(
    "/{assignmentId}",
    status_code=HTTPStatus.OK,
    response_model=EnrollmentPolicyAssignmentResponse,
    dependencies=[require_role("enrollment_policy_assignments:read")],
)
async def get_enrollment_policy_assignment(
    assignmentId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return EnrollmentPolicyAssignmentsController(db_manager).find_by_id(
        assignment_id=assignmentId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[EnrollmentPolicyAssignmentResponse],
    dependencies=[require_role("enrollment_policy_assignments:read")],
)
async def list_enrollment_policy_assignments(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
    enrollmentId: Optional[int] = None,
    templateId: Optional[int] = None,
    targetDate: Optional[date] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return EnrollmentPolicyAssignmentsController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        enrollment_id=enrollmentId,
        template_id=templateId,
        target_date=targetDate,
    )


@router.put(
    "/{assignmentId}",
    status_code=HTTPStatus.OK,
    response_model=EnrollmentPolicyAssignmentResponse,
    dependencies=[require_role("enrollment_policy_assignments:edit")],
)
async def update_enrollment_policy_assignment(
    assignmentId: int,
    data: UpdateEnrollmentPolicyAssignmentRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return EnrollmentPolicyAssignmentsController(db_manager).update(
        assignment_id=assignmentId,
        tenant_id=current_user.tenant_id,
        data=data,
    )


@router.delete(
    "/{assignmentId}",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("enrollment_policy_assignments:write")],
)
async def delete_enrollment_policy_assignment(
    assignmentId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    EnrollmentPolicyAssignmentsController(db_manager).delete(
        assignment_id=assignmentId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(message="Enrollment policy assignment deleted successfully")
