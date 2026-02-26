from datetime import date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .employee_enrollment import EmployeeEnrollment
    from .work_policy_template import WorkPolicyTemplate


class EnrollmentPolicyAssignment:
    id: int
    tenant_id: int
    enrollment_id: int
    template_id: int
    effective_from: date
    effective_to: Optional[date]

    enrollment: "EmployeeEnrollment"
    template: "WorkPolicyTemplate"

    def __init__(
        self,
        tenant_id: int,
        enrollment_id: int,
        template_id: int,
        effective_from: date,
        effective_to: Optional[date] = None,
    ):
        self.tenant_id = tenant_id
        self.enrollment_id = enrollment_id
        self.template_id = template_id
        self.effective_from = effective_from
        self.effective_to = effective_to
