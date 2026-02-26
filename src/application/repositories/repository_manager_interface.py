from abc import ABC, abstractmethod

from .bank_hours_ledger_repository_interface import BankHoursLedgerRepositoryInterface
from .daily_attendance_summary_repository_interface import (
    DailyAttendanceSummaryRepositoryInterface,
)
from .employee_enrollment_repository_interface import EmployeeEnrollmentRepositoryInterface
from .enrollment_policy_assignment_repository_interface import (
    EnrollmentPolicyAssignmentRepositoryInterface,
)
from .time_adjustment_item_repository_interface import TimeAdjustmentItemRepositoryInterface
from .time_adjustment_request_repository_interface import (
    TimeAdjustmentRequestRepositoryInterface,
)
from .time_punch_repository_interface import TimePunchRepositoryInterface
from .work_policy_template_repository_interface import WorkPolicyTemplateRepositoryInterface


class RepositoryManagerInterface(ABC):
    @abstractmethod
    def employee_enrollment_repository(self) -> EmployeeEnrollmentRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def work_policy_template_repository(self) -> WorkPolicyTemplateRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def enrollment_policy_assignment_repository(
        self,
    ) -> EnrollmentPolicyAssignmentRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def time_punch_repository(self) -> TimePunchRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def time_adjustment_request_repository(self) -> TimeAdjustmentRequestRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def time_adjustment_item_repository(self) -> TimeAdjustmentItemRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def daily_attendance_summary_repository(
        self,
    ) -> DailyAttendanceSummaryRepositoryInterface:
        raise NotImplementedError

    @abstractmethod
    def bank_hours_ledger_repository(self) -> BankHoursLedgerRepositoryInterface:
        raise NotImplementedError
