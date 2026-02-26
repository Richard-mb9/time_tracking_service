from application.dtos import CreateEnrollmentPolicyAssignmentDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from application.usecases.employee_enrollments import FindEmployeeEnrollmentByIdUseCase
from application.usecases.work_policy_templates import FindWorkPolicyTemplateByIdUseCase
from domain import EnrollmentPolicyAssignment


class CreateEnrollmentPolicyAssignmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.enrollment_policy_assignment_repository = (
            repository_manager.enrollment_policy_assignment_repository()
        )
        self.find_enrollment_by_id = FindEmployeeEnrollmentByIdUseCase(repository_manager)
        self.find_template_by_id = FindWorkPolicyTemplateByIdUseCase(repository_manager)

    def execute(
        self, data: CreateEnrollmentPolicyAssignmentDTO
    ) -> EnrollmentPolicyAssignment:
        enrollment = self.find_enrollment_by_id.execute(
            enrollment_id=data.enrollment_id,
            raise_if_is_none=True,
        )
        if enrollment.tenant_id != data.tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")

        template = self.find_template_by_id.execute(
            template_id=data.template_id,
            raise_if_is_none=True,
        )
        if template.tenant_id != data.tenant_id:
            raise BadRequestError("Template does not belong to tenant.")

        if data.effective_to is not None and data.effective_to < data.effective_from:
            raise BadRequestError("effective_to must be greater than or equal to effective_from.")

        overlapping = self.enrollment_policy_assignment_repository.find_overlapping(
            enrollment_id=data.enrollment_id,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
        )
        if len(overlapping) > 0:
            raise ConflictError("Assignment period overlaps with an existing assignment.")

        assignment = EnrollmentPolicyAssignment(
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            template_id=data.template_id,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
        )
        return self.enrollment_policy_assignment_repository.create(assignment)
