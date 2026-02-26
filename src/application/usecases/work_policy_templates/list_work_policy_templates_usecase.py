from application.dtos import ListWorkPolicyTemplatesDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import WorkPolicyTemplate


class ListWorkPolicyTemplatesUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.work_policy_template_repository = (
            repository_manager.work_policy_template_repository()
        )

    def execute(self, data: ListWorkPolicyTemplatesDTO) -> PaginatedResult[WorkPolicyTemplate]:
        result = self.work_policy_template_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            name=data.name,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
