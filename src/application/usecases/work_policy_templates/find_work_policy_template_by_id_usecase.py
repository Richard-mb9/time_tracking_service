from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import WorkPolicyTemplate


class FindWorkPolicyTemplateByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.work_policy_template_repository = (
            repository_manager.work_policy_template_repository()
        )

    @overload
    def execute(self, template_id: int) -> Optional[WorkPolicyTemplate]:
        pass

    @overload
    def execute(
        self, template_id: int, raise_if_is_none: Literal[True]
    ) -> WorkPolicyTemplate:
        pass

    @overload
    def execute(
        self, template_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[WorkPolicyTemplate]:
        pass

    def execute(self, template_id: int, raise_if_is_none: bool = False):
        template = self.work_policy_template_repository.find_by_id(template_id)
        if raise_if_is_none and template is None:
            raise NotFoundError("Work policy template not found.")
        return template
