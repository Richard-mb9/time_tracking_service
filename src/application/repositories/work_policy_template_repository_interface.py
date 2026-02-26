from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from application.repositories.types import DBPaginatedResult
from domain import WorkPolicyTemplate


class WorkPolicyTemplateRepositoryInterface(ABC):
    @abstractmethod
    def create(self, template: WorkPolicyTemplate) -> WorkPolicyTemplate:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, template_id: int, data: Dict[str, Any]
    ) -> Optional[WorkPolicyTemplate]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, template_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, template_id: int) -> Optional[WorkPolicyTemplate]:
        raise NotImplementedError

    @abstractmethod
    def find_by_name(
        self, tenant_id: int, name: str
    ) -> Optional[WorkPolicyTemplate]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> DBPaginatedResult[WorkPolicyTemplate]:
        raise NotImplementedError
