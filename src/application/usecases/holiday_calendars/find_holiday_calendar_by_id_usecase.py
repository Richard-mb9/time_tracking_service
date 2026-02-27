from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import HolidayCalendar


class FindHolidayCalendarByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()

    @overload
    def execute(self, holiday_calendar_id: int) -> Optional[HolidayCalendar]:
        pass

    @overload
    def execute(
        self, holiday_calendar_id: int, raise_if_is_none: Literal[True]
    ) -> HolidayCalendar:
        pass

    @overload
    def execute(
        self, holiday_calendar_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[HolidayCalendar]:
        pass

    def execute(self, holiday_calendar_id: int, raise_if_is_none: bool = False):
        holiday_calendar = self.holiday_calendar_repository.find_by_id(holiday_calendar_id)
        if raise_if_is_none and holiday_calendar is None:
            raise NotFoundError("Holiday calendar not found.")
        return holiday_calendar
