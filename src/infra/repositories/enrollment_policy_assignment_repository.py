from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import or_

from application.repositories import EnrollmentPolicyAssignmentRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import EnrollmentPolicyAssignment
from infra.database_manager import DatabaseManagerConnection


class EnrollmentPolicyAssignmentRepository(EnrollmentPolicyAssignmentRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(
        self, assignment: EnrollmentPolicyAssignment
    ) -> EnrollmentPolicyAssignment:
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def update(
        self, assignment_id: int, data: Dict[str, Any]
    ) -> Optional[EnrollmentPolicyAssignment]:
        assignment = self.find_by_id(assignment_id)
        if assignment is None:
            return None

        for key, value in data.items():
            setattr(assignment, key, value)

        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def delete(self, assignment_id: int) -> None:
        assignment = self.find_by_id(assignment_id)
        if assignment is None:
            return
        self.session.delete(assignment)
        self.session.commit()

    def find_by_id(self, assignment_id: int) -> Optional[EnrollmentPolicyAssignment]:
        return (
            self.session.query(EnrollmentPolicyAssignment)
            .filter(EnrollmentPolicyAssignment.id == assignment_id)
            .first()
        )

    def find_current_by_enrollment_and_date(
        self, enrollment_id: int, reference_date: date
    ) -> Optional[EnrollmentPolicyAssignment]:
        return (
            self.session.query(EnrollmentPolicyAssignment)
            .filter(EnrollmentPolicyAssignment.enrollment_id == enrollment_id)
            .filter(EnrollmentPolicyAssignment.effective_from <= reference_date)
            .filter(
                or_(
                    EnrollmentPolicyAssignment.effective_to.is_(None),
                    EnrollmentPolicyAssignment.effective_to >= reference_date,
                )
            )
            .order_by(EnrollmentPolicyAssignment.effective_from.desc())
            .first()
        )

    def find_overlapping(
        self,
        enrollment_id: int,
        effective_from: date,
        effective_to: Optional[date],
        exclude_assignment_id: Optional[int] = None,
    ) -> List[EnrollmentPolicyAssignment]:
        query = self.session.query(EnrollmentPolicyAssignment).filter(
            EnrollmentPolicyAssignment.enrollment_id == enrollment_id
        )

        if exclude_assignment_id is not None:
            query = query.filter(EnrollmentPolicyAssignment.id != exclude_assignment_id)

        if effective_to is not None:
            query = query.filter(
                EnrollmentPolicyAssignment.effective_from <= effective_to
            )

        query = query.filter(
            or_(
                EnrollmentPolicyAssignment.effective_to.is_(None),
                EnrollmentPolicyAssignment.effective_to >= effective_from,
            )
        )

        return query.all()

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        enrollment_id: Optional[int] = None,
        template_id: Optional[int] = None,
        target_date: Optional[date] = None,
    ) -> DBPaginatedResult[EnrollmentPolicyAssignment]:
        query = self.session.query(EnrollmentPolicyAssignment)

        if tenant_id is not None:
            query = query.filter(EnrollmentPolicyAssignment.tenant_id == tenant_id)

        if enrollment_id is not None:
            query = query.filter(
                EnrollmentPolicyAssignment.enrollment_id == enrollment_id
            )

        if template_id is not None:
            query = query.filter(EnrollmentPolicyAssignment.template_id == template_id)

        if target_date is not None:
            query = query.filter(EnrollmentPolicyAssignment.effective_from <= target_date)
            query = query.filter(
                or_(
                    EnrollmentPolicyAssignment.effective_to.is_(None),
                    EnrollmentPolicyAssignment.effective_to >= target_date,
                )
            )

        total = query.count()
        data = (
            query.order_by(EnrollmentPolicyAssignment.effective_from.desc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(data=data, total_count=total)
