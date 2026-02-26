from typing import Optional

from api.schemas import (
    CreateEmployeeEnrollmentRequest,
    DefaultCreateResponse,
    EmployeeEnrollmentResponse,
    PaginatedResponse,
    UpdateEmployeeEnrollmentRequest,
)
from application.exceptions import BadRequestError
from application.dtos import (
    CreateEmployeeEnrollmentDTO,
    ListEmployeeEnrollmentsDTO,
    UpdateEmployeeEnrollmentDTO,
)
from application.usecases.employee_enrollments import (
    CreateEmployeeEnrollmentUseCase,
    DeleteEmployeeEnrollmentUseCase,
    FindEmployeeEnrollmentByIdUseCase,
    ListEmployeeEnrollmentsUseCase,
    UpdateEmployeeEnrollmentUseCase,
)
from domain import EmployeeEnrollment
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class EmployeeEnrollmentsController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateEmployeeEnrollmentRequest) -> DefaultCreateResponse:
        enrollment = CreateEmployeeEnrollmentUseCase(self.repository_manager).execute(
            CreateEmployeeEnrollmentDTO(
                tenant_id=data.tenantId,
                employee_id=data.employeeId,
                enrollment_code=data.enrollmentCode,
                active_from=data.activeFrom,
                active_to=data.activeTo,
                is_active=data.isActive,
            )
        )
        return DefaultCreateResponse(id=enrollment.id)

    def find_by_id(self, enrollment_id: int, tenant_id: int) -> EmployeeEnrollmentResponse:
        enrollment = FindEmployeeEnrollmentByIdUseCase(self.repository_manager).execute(
            enrollment_id=enrollment_id,
            raise_if_is_none=True,
        )
        if enrollment.tenant_id != tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")
        return self.__to_response(enrollment)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        employee_id: Optional[int],
        enrollment_code: Optional[str],
        is_active: Optional[bool],
    ) -> PaginatedResponse[EmployeeEnrollmentResponse]:
        result = ListEmployeeEnrollmentsUseCase(self.repository_manager).execute(
            ListEmployeeEnrollmentsDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                employee_id=employee_id,
                enrollment_code=enrollment_code,
                is_active=is_active,
            )
        )
        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def update(
        self,
        enrollment_id: int,
        tenant_id: int,
        data: UpdateEmployeeEnrollmentRequest,
    ) -> EmployeeEnrollmentResponse:
        enrollment = UpdateEmployeeEnrollmentUseCase(self.repository_manager).execute(
            enrollment_id=enrollment_id,
            tenant_id=tenant_id,
            data=UpdateEmployeeEnrollmentDTO(
                employee_id=data.employeeId,
                enrollment_code=data.enrollmentCode,
                active_from=data.activeFrom,
                active_to=data.activeTo,
                is_active=data.isActive,
            ),
        )
        return self.__to_response(enrollment)

    def delete(self, enrollment_id: int, tenant_id: int) -> None:
        DeleteEmployeeEnrollmentUseCase(self.repository_manager).execute(
            enrollment_id=enrollment_id,
            tenant_id=tenant_id,
        )

    def __to_response(self, item: EmployeeEnrollment) -> EmployeeEnrollmentResponse:
        return EmployeeEnrollmentResponse(
            id=item.id,
            tenantId=item.tenant_id,
            employeeId=item.employee_id,
            enrollmentCode=item.enrollment_code,
            activeFrom=item.active_from,
            activeTo=item.active_to,
            isActive=item.is_active,
        )
