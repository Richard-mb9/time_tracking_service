from typing import TYPE_CHECKING

from .enums import WorkWeekDay

if TYPE_CHECKING:  # pragma: no cover
    from .work_policy_template import WorkPolicyTemplate


class WorkDayPolicy:
    id: int
    work_policy_template_id: int
    daily_work_minutes: int
    break_minutes: int
    week_day: WorkWeekDay

    work_policy_template: "WorkPolicyTemplate"

    def __init__(
        self,
        work_policy_template_id: int,
        daily_work_minutes: int,
        break_minutes: int,
        week_day: WorkWeekDay,
    ):
        self.work_policy_template_id = work_policy_template_id
        self.daily_work_minutes = daily_work_minutes
        self.break_minutes = break_minutes
        self.week_day = week_day
