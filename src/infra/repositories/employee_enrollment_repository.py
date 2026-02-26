from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func

from application.repositories import EmployeeEnrollmentRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import EmployeeEnrollment, TimePunch
from infra.database_manager import DatabaseManagerConnection


class EmployeeEnrollmentRepository(EmployeeEnrollmentRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(self, enrollment: EmployeeEnrollment) -> EmployeeEnrollment:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    def update(
        self, enrollment_id: int, data: Dict[str, Any]
    ) -> Optional[EmployeeEnrollment]:
        enrollment = self.find_by_id(enrollment_id)
        if enrollment is None:
            return None

        for key, value in data.items():
            setattr(enrollment, key, value)

        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    def delete(self, enrollment_id: int) -> None:
        enrollment = self.find_by_id(enrollment_id)
        if enrollment is None:
            return
        self.session.delete(enrollment)
        self.session.commit()

    def find_by_id(self, enrollment_id: int) -> Optional[EmployeeEnrollment]:
        return (
            self.session.query(EmployeeEnrollment)
            .filter(EmployeeEnrollment.id == enrollment_id)
            .first()
        )

    def find_by_code(
        self, tenant_id: int, enrollment_code: str
    ) -> Optional[EmployeeEnrollment]:
        return (
            self.session.query(EmployeeEnrollment)
            .filter(EmployeeEnrollment.tenant_id == tenant_id)
            .filter(EmployeeEnrollment.enrollment_code == enrollment_code)
            .first()
        )

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        enrollment_code: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> DBPaginatedResult[EmployeeEnrollment]:
        query = self.session.query(EmployeeEnrollment)

        if tenant_id is not None:
            query = query.filter(EmployeeEnrollment.tenant_id == tenant_id)

        if employee_id is not None:
            query = query.filter(EmployeeEnrollment.employee_id == employee_id)

        if enrollment_code is not None:
            query = query.filter(
                EmployeeEnrollment.enrollment_code.ilike(f"%{enrollment_code}%")
            )

        if is_active is not None:
            query = query.filter(EmployeeEnrollment.is_active == is_active)

        total = query.count()
        data = (
            query.order_by(EmployeeEnrollment.id.asc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(data=data, total_count=total)

    def find_other_enrollments_with_punch_on_date(
        self,
        tenant_id: int,
        employee_id: int,
        work_date: date,
        exclude_enrollment_id: int,
    ) -> List[EmployeeEnrollment]:
        return (
            self.session.query(EmployeeEnrollment)
            .join(TimePunch, TimePunch.enrollment_id == EmployeeEnrollment.id)
            .filter(EmployeeEnrollment.tenant_id == tenant_id)
            .filter(EmployeeEnrollment.employee_id == employee_id)
            .filter(EmployeeEnrollment.id != exclude_enrollment_id)
            .filter(func.date(TimePunch.punched_at) == work_date)
            .distinct()
            .all()
        )
