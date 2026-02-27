from dataclasses import dataclass

from domain import WorkWeekDay


@dataclass
class WorkDayPolicyDTO:
    week_day: WorkWeekDay
    daily_work_minutes: int
    break_minutes: int
