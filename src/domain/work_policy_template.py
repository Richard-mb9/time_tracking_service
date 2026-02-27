from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .enrollment_policy_assignment import EnrollmentPolicyAssignment
    from .work_day_policy import WorkDayPolicy

from .enums import WorkWeekDay


class WorkPolicyTemplate:
    id: int
    tenant_id: int
    name: str
    work_day_policies: List["WorkDayPolicy"]

    assignments: List["EnrollmentPolicyAssignment"]

    def __init__(
        self,
        tenant_id: int,
        name: str,
        work_day_policies: Optional[List["WorkDayPolicy"]] = None,
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.work_day_policies = work_day_policies or []
        self.assignments = []

    def find_work_day_policy(self, week_day: WorkWeekDay) -> Optional["WorkDayPolicy"]:
        return next(
            (
                policy
                for policy in self.work_day_policies
                if (
                    WorkWeekDay(policy.week_day)
                    if isinstance(policy.week_day, str)
                    else policy.week_day
                )
                == week_day
            ),
            None,
        )
