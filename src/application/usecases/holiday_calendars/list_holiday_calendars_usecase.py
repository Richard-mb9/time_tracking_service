from application.dtos import ListHolidayCalendarsDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import HolidayCalendar


class ListHolidayCalendarsUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()

    def execute(self, data: ListHolidayCalendarsDTO) -> PaginatedResult[HolidayCalendar]:
        result = self.holiday_calendar_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            name=data.name,
            city=data.city,
            uf=data.uf,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            national=data.national,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
