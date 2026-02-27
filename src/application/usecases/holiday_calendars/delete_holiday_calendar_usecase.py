from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface

from .find_holiday_calendar_by_id_usecase import FindHolidayCalendarByIdUseCase


class DeleteHolidayCalendarUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()
        self.find_by_id_usecase = FindHolidayCalendarByIdUseCase(repository_manager)

    def execute(self, holiday_calendar_id: int, tenant_id: int) -> None:
        holiday_calendar = self.find_by_id_usecase.execute(
            holiday_calendar_id=holiday_calendar_id,
            raise_if_is_none=True,
        )
        if holiday_calendar.tenant_id != tenant_id:
            raise BadRequestError("Holiday calendar does not belong to tenant.")
        self.holiday_calendar_repository.delete(holiday_calendar_id)
