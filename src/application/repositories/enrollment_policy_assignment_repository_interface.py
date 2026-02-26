from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from application.repositories.types import DBPaginatedResult
from domain import EnrollmentPolicyAssignment


class EnrollmentPolicyAssignmentRepositoryInterface(ABC):
    @abstractmethod
    def create(
        self, assignment: EnrollmentPolicyAssignment
    ) -> EnrollmentPolicyAssignment:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, assignment_id: int, data: Dict[str, Any]
    ) -> Optional[EnrollmentPolicyAssignment]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, assignment_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, assignment_id: int) -> Optional[EnrollmentPolicyAssignment]:
        raise NotImplementedError

    @abstractmethod
    def find_current_by_enrollment_and_date(
        self, enrollment_id: int, reference_date: date
    ) -> Optional[EnrollmentPolicyAssignment]:
        raise NotImplementedError

    @abstractmethod
    def find_overlapping(
        self,
        enrollment_id: int,
        effective_from: date,
        effective_to: Optional[date],
        exclude_assignment_id: Optional[int] = None,
    ) -> List[EnrollmentPolicyAssignment]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        enrollment_id: Optional[int] = None,
        template_id: Optional[int] = None,
        target_date: Optional[date] = None,
    ) -> DBPaginatedResult[EnrollmentPolicyAssignment]:
        raise NotImplementedError
