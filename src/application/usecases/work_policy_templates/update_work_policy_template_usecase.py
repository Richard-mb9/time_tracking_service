from typing import Any, Dict

from application.dtos import UpdateWorkPolicyTemplateDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import WorkPolicyTemplate

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

        daily_work_minutes = (
            data.daily_work_minutes
            if data.daily_work_minutes is not None
            else template.daily_work_minutes
        )
        break_minutes = (
            data.break_minutes if data.break_minutes is not None else template.break_minutes
        )

        if daily_work_minutes <= 0:
            raise BadRequestError("daily_work_minutes must be greater than zero.")

        if break_minutes < 0:
            raise BadRequestError("break_minutes must be greater than or equal to zero.")

        if break_minutes > daily_work_minutes:
            raise BadRequestError("break_minutes must be less than daily_work_minutes.")

        if data.daily_work_minutes is not None:
            data_to_update["daily_work_minutes"] = data.daily_work_minutes

        if data.break_minutes is not None:
            data_to_update["break_minutes"] = data.break_minutes

        if len(data_to_update) == 0:
            return template

        updated = self.work_policy_template_repository.update(template_id, data_to_update)
        if updated is None:
            raise BadRequestError("Unable to update template.")
        return updated
