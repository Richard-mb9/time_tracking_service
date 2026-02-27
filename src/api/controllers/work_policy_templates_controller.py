from typing import List, Optional

from api.schemas import (
    CreateWorkPolicyTemplateRequest,
    DefaultCreateResponse,
    PaginatedResponse,
    UpdateWorkPolicyTemplateRequest,
    WorkDayPolicyResponse,
    WorkPolicyTemplateResponse,
)
from application.exceptions import BadRequestError
from application.dtos import (
    CreateWorkPolicyTemplateDTO,
    ListWorkPolicyTemplatesDTO,
    UpdateWorkPolicyTemplateDTO,
    WorkDayPolicyDTO,
)
from application.usecases.work_policy_templates import (
    CreateWorkPolicyTemplateUseCase,
    DeleteWorkPolicyTemplateUseCase,
    FindWorkPolicyTemplateByIdUseCase,
    ListWorkPolicyTemplatesUseCase,
    UpdateWorkPolicyTemplateUseCase,
)
from domain import WorkDayPolicy, WorkPolicyTemplate, WorkWeekDay
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
                work_day_policies=[
                    WorkDayPolicyDTO(
                        week_day=WorkWeekDay(policy.weekDay.value),
                        daily_work_minutes=policy.dailyWorkMinutes,
                        break_minutes=policy.breakMinutes,
                    )
                    for policy in data.workDayPolicies
                ],
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
                work_day_policies=(
                    [
                        WorkDayPolicyDTO(
                            week_day=WorkWeekDay(policy.weekDay.value),
                            daily_work_minutes=policy.dailyWorkMinutes,
                            break_minutes=policy.breakMinutes,
                        )
                        for policy in data.workDayPolicies
                    ]
                    if data.workDayPolicies is not None
                    else None
                ),
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
            workDayPolicies=[
                self.__to_work_day_policy_response(policy)
                for policy in self.__sort_work_day_policies(item.work_day_policies)
            ],
        )

    def __to_work_day_policy_response(self, item: WorkDayPolicy) -> WorkDayPolicyResponse:
        return WorkDayPolicyResponse(
            id=item.id,
            weekDay=item.week_day.value if hasattr(item.week_day, "value") else item.week_day,
            dailyWorkMinutes=item.daily_work_minutes,
            breakMinutes=item.break_minutes,
        )

    def __sort_work_day_policies(self, data: List[WorkDayPolicy]) -> List[WorkDayPolicy]:
        order = {
            WorkWeekDay.MONDAY: 1,
            WorkWeekDay.TUESDAY: 2,
            WorkWeekDay.WEDNESDAY: 3,
            WorkWeekDay.THURSDAY: 4,
            WorkWeekDay.FRIDAY: 5,
            WorkWeekDay.SATURDAY: 6,
            WorkWeekDay.SUNDAY: 7,
        }
        return sorted(
            data,
            key=lambda item: order.get(
                WorkWeekDay(item.week_day)
                if isinstance(item.week_day, str)
                else item.week_day,
                99,
            ),
        )
