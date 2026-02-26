from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query

from api.controllers import WorkPolicyTemplatesController
from api.routers.dependencies import (
    CurrentUser,
    DBManager,
    require_role,
    resolve_tenant_id,
)
from api.schemas import (
    CreateWorkPolicyTemplateRequest,
    DefaultCreateResponse,
    DefaultResponse,
    PaginatedResponse,
    UpdateWorkPolicyTemplateRequest,
    WorkPolicyTemplateResponse,
)

router = APIRouter()


@router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=DefaultCreateResponse,
    dependencies=[require_role("work_policy_templates:create")],
)
async def create_work_policy_template(
    data: CreateWorkPolicyTemplateRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    _ = current_user
    return WorkPolicyTemplatesController(db_manager).create(data)


@router.get(
    "/{templateId}",
    status_code=HTTPStatus.OK,
    response_model=WorkPolicyTemplateResponse,
    dependencies=[require_role("work_policy_templates:read")],
)
async def get_work_policy_template(
    templateId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return WorkPolicyTemplatesController(db_manager).find_by_id(
        template_id=templateId,
        tenant_id=current_user.tenant_id,
    )


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=PaginatedResponse[WorkPolicyTemplateResponse],
    dependencies=[require_role("work_policy_templates:read")],
)
async def list_work_policy_templates(
    db_manager: DBManager,
    current_user: CurrentUser,
    page: int = Query(default=0, ge=0),
    perPage: int = Query(default=20, ge=1, le=100),
    name: Optional[str] = None,
    tenantId: Optional[int] = None,
):
    tenant_id = resolve_tenant_id(current_user, tenantId)
    return WorkPolicyTemplatesController(db_manager).list_all(
        requester_tenant_id=tenant_id,
        page=page,
        per_page=perPage,
        name=name,
    )


@router.put(
    "/{templateId}",
    status_code=HTTPStatus.OK,
    response_model=WorkPolicyTemplateResponse,
    dependencies=[require_role("work_policy_templates:edit")],
)
async def update_work_policy_template(
    templateId: int,
    data: UpdateWorkPolicyTemplateRequest,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    return WorkPolicyTemplatesController(db_manager).update(
        template_id=templateId,
        tenant_id=current_user.tenant_id,
        data=data,
    )


@router.delete(
    "/{templateId}",
    status_code=HTTPStatus.OK,
    response_model=DefaultResponse,
    dependencies=[require_role("work_policy_templates:write")],
)
async def delete_work_policy_template(
    templateId: int,
    db_manager: DBManager,
    current_user: CurrentUser,
):
    WorkPolicyTemplatesController(db_manager).delete(
        template_id=templateId,
        tenant_id=current_user.tenant_id,
    )
    return DefaultResponse(message="Work policy template deleted successfully")
