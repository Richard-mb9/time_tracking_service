from typing import Optional

from api.schemas import (
    CreateWorkPolicyTemplateRequest,
    DefaultCreateResponse,
    PaginatedResponse,
    UpdateWorkPolicyTemplateRequest,
    WorkPolicyTemplateResponse,
)
from application.exceptions import BadRequestError
from application.dtos import (
    CreateWorkPolicyTemplateDTO,
    ListWorkPolicyTemplatesDTO,
    UpdateWorkPolicyTemplateDTO,
)
from application.usecases.work_policy_templates import (
    CreateWorkPolicyTemplateUseCase,
    DeleteWorkPolicyTemplateUseCase,
    FindWorkPolicyTemplateByIdUseCase,
    ListWorkPolicyTemplatesUseCase,
    UpdateWorkPolicyTemplateUseCase,
)
from domain import WorkPolicyTemplate
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class WorkPolicyTemplatesController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateWorkPolicyTemplateRequest) -> DefaultCreateResponse:
        template = CreateWorkPolicyTemplateUseCase(self.repository_manager).execute(
            CreateWorkPolicyTemplateDTO(
                tenant_id=data.tenantId,
                name=data.name,
                daily_work_minutes=data.dailyWorkMinutes,
                break_minutes=data.breakMinutes,
            )
        )
        return DefaultCreateResponse(id=template.id)

    def find_by_id(self, template_id: int, tenant_id: int) -> WorkPolicyTemplateResponse:
        template = FindWorkPolicyTemplateByIdUseCase(self.repository_manager).execute(
            template_id=template_id,
            raise_if_is_none=True,
        )
        if template.tenant_id != tenant_id:
            raise BadRequestError("Template does not belong to tenant.")
        return self.__to_response(template)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        name: Optional[str],
    ) -> PaginatedResponse[WorkPolicyTemplateResponse]:
        result = ListWorkPolicyTemplatesUseCase(self.repository_manager).execute(
            ListWorkPolicyTemplatesDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                name=name,
            )
        )
        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def update(
        self,
        template_id: int,
        tenant_id: int,
        data: UpdateWorkPolicyTemplateRequest,
    ) -> WorkPolicyTemplateResponse:
        template = UpdateWorkPolicyTemplateUseCase(self.repository_manager).execute(
            template_id=template_id,
            tenant_id=tenant_id,
            data=UpdateWorkPolicyTemplateDTO(
                name=data.name,
                daily_work_minutes=data.dailyWorkMinutes,
                break_minutes=data.breakMinutes,
            ),
        )
        return self.__to_response(template)

    def delete(self, template_id: int, tenant_id: int) -> None:
        DeleteWorkPolicyTemplateUseCase(self.repository_manager).execute(
            template_id=template_id,
            tenant_id=tenant_id,
        )

    def __to_response(self, item: WorkPolicyTemplate) -> WorkPolicyTemplateResponse:
        return WorkPolicyTemplateResponse(
            id=item.id,
            tenantId=item.tenant_id,
            name=item.name,
            dailyWorkMinutes=item.daily_work_minutes,
            breakMinutes=item.break_minutes,
        )
