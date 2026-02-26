from application.repositories import RepositoryManagerInterface
from application.repositories.bank_hours_ledger_repository_interface import (
    BankHoursLedgerRepositoryInterface,
)
from application.repositories.daily_attendance_summary_repository_interface import (
    DailyAttendanceSummaryRepositoryInterface,
)
from application.repositories.enrollment_policy_assignment_repository_interface import (
    EnrollmentPolicyAssignmentRepositoryInterface,
)
from application.repositories.time_adjustment_item_repository_interface import (
    TimeAdjustmentItemRepositoryInterface,
)
from application.repositories.time_adjustment_request_repository_interface import (
    TimeAdjustmentRequestRepositoryInterface,
)
from application.repositories.time_punch_repository_interface import (
    TimePunchRepositoryInterface,
)
from application.repositories.work_policy_template_repository_interface import (
    WorkPolicyTemplateRepositoryInterface,
)
from infra.database_manager import DatabaseManagerConnection

from .bank_hours_ledger_repository import BankHoursLedgerRepository
from .daily_attendance_summary_repository import DailyAttendanceSummaryRepository
from .enrollment_policy_assignment_repository import EnrollmentPolicyAssignmentRepository
from .time_adjustment_item_repository import TimeAdjustmentItemRepository
from .time_adjustment_request_repository import TimeAdjustmentRequestRepository
from .time_punch_repository import TimePunchRepository
from .work_policy_template_repository import WorkPolicyTemplateRepository


class RepositoryManager(RepositoryManagerInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.db_manager = db_manager

    def work_policy_template_repository(self) -> WorkPolicyTemplateRepositoryInterface:
        return WorkPolicyTemplateRepository(self.db_manager)

    def enrollment_policy_assignment_repository(
        self,
    ) -> EnrollmentPolicyAssignmentRepositoryInterface:
        return EnrollmentPolicyAssignmentRepository(self.db_manager)

    def time_punch_repository(self) -> TimePunchRepositoryInterface:
        return TimePunchRepository(self.db_manager)

    def time_adjustment_request_repository(self) -> TimeAdjustmentRequestRepositoryInterface:
        return TimeAdjustmentRequestRepository(self.db_manager)

    def time_adjustment_item_repository(self) -> TimeAdjustmentItemRepositoryInterface:
        return TimeAdjustmentItemRepository(self.db_manager)

    def daily_attendance_summary_repository(
        self,
    ) -> DailyAttendanceSummaryRepositoryInterface:
        return DailyAttendanceSummaryRepository(self.db_manager)

    def bank_hours_ledger_repository(self) -> BankHoursLedgerRepositoryInterface:
        return BankHoursLedgerRepository(self.db_manager)
