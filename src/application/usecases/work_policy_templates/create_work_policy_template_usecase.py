from typing import List

from application.dtos import CreateWorkPolicyTemplateDTO, WorkDayPolicyDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import WorkDayPolicy, WorkPolicyTemplate


class CreateWorkPolicyTemplateUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.work_policy_template_repository = (
            repository_manager.work_policy_template_repository()
        )

    def execute(self, data: CreateWorkPolicyTemplateDTO) -> WorkPolicyTemplate:
        name = data.name.strip()
        if len(name) == 0:
            raise BadRequestError("Template name is required.")

        self.__validate_work_day_policies(data.work_day_policies)

        existing = self.work_policy_template_repository.find_by_name(
            tenant_id=data.tenant_id,
            name=name,
        )
        if existing is not None:
            raise ConflictError("Template name already exists for this tenant.")

        template = WorkPolicyTemplate(
            tenant_id=data.tenant_id,
            name=name,
            work_day_policies=[
                WorkDayPolicy(
                    work_policy_template_id=0,
                    daily_work_minutes=policy.daily_work_minutes,
                    break_minutes=policy.break_minutes,
                    week_day=policy.week_day,
                )
                for policy in data.work_day_policies
            ],
        )
        return self.work_policy_template_repository.create(template)

    def __validate_work_day_policies(
        self, work_day_policies: List[WorkDayPolicyDTO]
    ) -> None:
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
