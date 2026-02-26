from typing import List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .enrollment_policy_assignment import EnrollmentPolicyAssignment


class WorkPolicyTemplate:
    id: int
    tenant_id: int
    name: str
    daily_work_minutes: int
    break_minutes: int

    assignments: List["EnrollmentPolicyAssignment"]

    def __init__(
        self,
        tenant_id: int,
        name: str,
        daily_work_minutes: int,
        break_minutes: int,
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.daily_work_minutes = daily_work_minutes
        self.break_minutes = break_minutes
        self.assignments = []
