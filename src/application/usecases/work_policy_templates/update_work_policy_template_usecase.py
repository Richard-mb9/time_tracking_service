from typing import Any, Dict, List

from application.dtos import UpdateWorkPolicyTemplateDTO, WorkDayPolicyDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import WorkDayPolicy, WorkPolicyTemplate

from .find_work_policy_template_by_id_usecase import FindWorkPolicyTemplateByIdUseCase


class UpdateWorkPolicyTemplateUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.work_policy_template_repository = (
            repository_manager.work_policy_template_repository()
        )
        self.find_by_id_usecase = FindWorkPolicyTemplateByIdUseCase(repository_manager)

    def execute(
        self, template_id: int, tenant_id: int, data: UpdateWorkPolicyTemplateDTO
    ) -> WorkPolicyTemplate:
        template = self.find_by_id_usecase.execute(
            template_id=template_id,
            raise_if_is_none=True,
        )
        if template.tenant_id != tenant_id:
            raise BadRequestError("Template does not belong to tenant.")

        data_to_update: Dict[str, Any] = {}

        if data.name is not None:
            name = data.name.strip()
            if len(name) == 0:
                raise BadRequestError("Template name is required.")
            existing = self.work_policy_template_repository.find_by_name(
                tenant_id=template.tenant_id,
                name=name,
            )
            if existing is not None and existing.id != template.id:
                raise ConflictError("Template name already exists for this tenant.")
            data_to_update["name"] = name

        if data.work_day_policies is not None:
            self.__validate_work_day_policies(data.work_day_policies)
            data_to_update["work_day_policies"] = [
                WorkDayPolicy(
                    work_policy_template_id=template.id,
                    daily_work_minutes=policy.daily_work_minutes,
                    break_minutes=policy.break_minutes,
                    week_day=policy.week_day,
                )
                for policy in data.work_day_policies
            ]

        if len(data_to_update) == 0:
            return template

        updated = self.work_policy_template_repository.update(template_id, data_to_update)
        if updated is None:
            raise BadRequestError("Unable to update template.")
        return updated

    def __validate_work_day_policies(self, work_day_policies: List[WorkDayPolicyDTO]) -> None:
        if len(work_day_policies) == 0:
            raise BadRequestError("At least one work day policy is required.")

        used_week_days = set()
        for policy in work_day_policies:
            if policy.week_day in used_week_days:
                raise BadRequestError("Duplicated week_day in work_day_policies.")

            if policy.daily_work_minutes <= 0:
                raise BadRequestError("daily_work_minutes must be greater than zero.")

            if policy.break_minutes < 0:
                raise BadRequestError("break_minutes must be greater than or equal to zero.")

            if policy.break_minutes > policy.daily_work_minutes:
                raise BadRequestError("break_minutes must be less than daily_work_minutes.")

            used_week_days.add(policy.week_day)
