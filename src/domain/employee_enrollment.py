from datetime import date
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .bank_hours_ledger import BankHoursLedger
    from .daily_attendance_summary import DailyAttendanceSummary
    from .enrollment_policy_assignment import EnrollmentPolicyAssignment
    from .time_adjustment_request import TimeAdjustmentRequest
    from .time_punch import TimePunch


class EmployeeEnrollment:
    id: int
    tenant_id: int
    employee_id: int
    enrollment_code: str
    active_from: date
    active_to: Optional[date]
    is_active: bool

    policy_assignments: List["EnrollmentPolicyAssignment"]
    time_punches: List["TimePunch"]
    adjustment_requests: List["TimeAdjustmentRequest"]
    daily_summaries: List["DailyAttendanceSummary"]
    bank_hours_entries: List["BankHoursLedger"]

    def __init__(
        self,
        tenant_id: int,
        employee_id: int,
        enrollment_code: str,
        active_from: date,
        active_to: Optional[date] = None,
        is_active: bool = True,
    ):
        self.tenant_id = tenant_id
        self.employee_id = employee_id
        self.enrollment_code = enrollment_code
        self.active_from = active_from
        self.active_to = active_to
        self.is_active = is_active
        self.policy_assignments = []
        self.time_punches = []
        self.adjustment_requests = []
        self.daily_summaries = []
        self.bank_hours_entries = []
