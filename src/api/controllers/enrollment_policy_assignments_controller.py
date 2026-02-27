from datetime import date
from typing import List, Optional

from api.schemas import (
    CreateEnrollmentPolicyAssignmentRequest,
    CreateEnrollmentPolicyAssignmentsRequest,
    DefaultCreateResponse,
    EnrollmentPolicyAssignmentResponse,
    PaginatedResponse,
    UpdateEnrollmentPolicyAssignmentRequest,
)
from application.exceptions import BadRequestError
from application.dtos import (
    CreateEnrollmentPolicyAssignmentDTO,
    CreateEnrollmentPolicyAssignmentsDTO,
    CreateEnrollmentPolicyAssignmentsItemDTO,
    ListEnrollmentPolicyAssignmentsDTO,
    UpdateEnrollmentPolicyAssignmentDTO,
)
from application.usecases.enrollment_policy_assignments import (
    CreateEnrollmentPolicyAssignmentUseCase,
    CreateEnrollmentPolicyAssignmentsUseCase,
    DeleteEnrollmentPolicyAssignmentUseCase,
    FindEnrollmentPolicyAssignmentByIdUseCase,
    ListEnrollmentPolicyAssignmentsUseCase,
    UpdateEnrollmentPolicyAssignmentUseCase,
)
from domain import EnrollmentPolicyAssignment
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class EnrollmentPolicyAssignmentsController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateEnrollmentPolicyAssignmentRequest) -> DefaultCreateResponse:
        assignment = CreateEnrollmentPolicyAssignmentUseCase(self.repository_manager).execute(
            CreateEnrollmentPolicyAssignmentDTO(
                tenant_id=data.tenantId,
                employee_id=data.employeeId,
                matricula=data.matricula,
                template_id=data.templateId,
                effective_from=data.effectiveFrom,
                effective_to=data.effectiveTo,
            )
        )
        return DefaultCreateResponse(id=assignment.id)

    def create_many(
        self, data: CreateEnrollmentPolicyAssignmentsRequest
    ) -> List[EnrollmentPolicyAssignmentResponse]:
        assignments = CreateEnrollmentPolicyAssignmentsUseCase(
            self.repository_manager
        ).execute(
            CreateEnrollmentPolicyAssignmentsDTO(
                tenant_id=data.tenantId,
                template_id=data.templateId,
                effective_from=data.effectiveFrom,
                effective_to=data.effectiveTo,
                employees=[
                    CreateEnrollmentPolicyAssignmentsItemDTO(
                        employee_id=item.employeeId,
                        matricula=item.matricula,
                    )
                    for item in data.employees
                ],
            )
        )
        return [self.__to_response(item) for item in assignments]

    def find_by_id(
        self, assignment_id: int, tenant_id: int
    ) -> EnrollmentPolicyAssignmentResponse:
        assignment = FindEnrollmentPolicyAssignmentByIdUseCase(
            self.repository_manager
        ).execute(assignment_id=assignment_id, raise_if_is_none=True)
        if assignment.tenant_id != tenant_id:
            raise BadRequestError("Assignment does not belong to tenant.")
        return self.__to_response(assignment)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        employee_id: Optional[int],
        matricula: Optional[str],
        template_id: Optional[int],
        target_date: Optional[date],
    ) -> PaginatedResponse[EnrollmentPolicyAssignmentResponse]:
        result = ListEnrollmentPolicyAssignmentsUseCase(self.repository_manager).execute(
            ListEnrollmentPolicyAssignmentsDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                employee_id=employee_id,
                matricula=matricula,
                template_id=template_id,
                target_date=target_date,
            )
        )
        return PaginatedResponse(
            data=[self.__to_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def update(
        self,
        assignment_id: int,
        tenant_id: int,
        data: UpdateEnrollmentPolicyAssignmentRequest,
    ) -> EnrollmentPolicyAssignmentResponse:
        assignment = UpdateEnrollmentPolicyAssignmentUseCase(self.repository_manager).execute(
            assignment_id=assignment_id,
            tenant_id=tenant_id,
            data=UpdateEnrollmentPolicyAssignmentDTO(
                template_id=data.templateId,
                effective_from=data.effectiveFrom,
                effective_to=data.effectiveTo,
            ),
        )
        return self.__to_response(assignment)

    def delete(self, assignment_id: int, tenant_id: int) -> None:
        DeleteEnrollmentPolicyAssignmentUseCase(self.repository_manager).execute(
            assignment_id=assignment_id,
            tenant_id=tenant_id,
        )

    def __to_response(
        self, item: EnrollmentPolicyAssignment
    ) -> EnrollmentPolicyAssignmentResponse:
        return EnrollmentPolicyAssignmentResponse(
            id=item.id,
            tenantId=item.tenant_id,
            employeeId=item.employee_id,
            matricula=item.matricula,
            templateId=item.template_id,
            effectiveFrom=item.effective_from,
            effectiveTo=item.effective_to,
        )
