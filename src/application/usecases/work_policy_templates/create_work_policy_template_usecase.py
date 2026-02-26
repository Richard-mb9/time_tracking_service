from application.dtos import CreateWorkPolicyTemplateDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import WorkPolicyTemplate


class CreateWorkPolicyTemplateUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.work_policy_template_repository = (
            repository_manager.work_policy_template_repository()
        )

    def execute(self, data: CreateWorkPolicyTemplateDTO) -> WorkPolicyTemplate:
        name = data.name.strip()
        if len(name) == 0:
            raise BadRequestError("Template name is required.")

        if data.daily_work_minutes <= 0:
            raise BadRequestError("daily_work_minutes must be greater than zero.")

        if data.break_minutes < 0:
            raise BadRequestError("break_minutes must be greater than or equal to zero.")

        if data.break_minutes > data.daily_work_minutes:
            raise BadRequestError("break_minutes must be less than daily_work_minutes.")

        existing = self.work_policy_template_repository.find_by_name(
            tenant_id=data.tenant_id,
            name=name,
        )
        if existing is not None:
            raise ConflictError("Template name already exists for this tenant.")

        template = WorkPolicyTemplate(
            tenant_id=data.tenant_id,
            name=name,
            daily_work_minutes=data.daily_work_minutes,
            break_minutes=data.break_minutes,
        )
        return self.work_policy_template_repository.create(template)
