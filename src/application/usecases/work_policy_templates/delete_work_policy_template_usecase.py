from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface

from .find_work_policy_template_by_id_usecase import FindWorkPolicyTemplateByIdUseCase


class DeleteWorkPolicyTemplateUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.work_policy_template_repository = (
            repository_manager.work_policy_template_repository()
        )
        self.find_by_id_usecase = FindWorkPolicyTemplateByIdUseCase(repository_manager)

    def execute(self, template_id: int, tenant_id: int) -> None:
        template = self.find_by_id_usecase.execute(
            template_id=template_id,
            raise_if_is_none=True,
        )
        if template.tenant_id != tenant_id:
            raise BadRequestError("Template does not belong to tenant.")
        self.work_policy_template_repository.delete(template_id)
