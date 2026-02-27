from typing import List

from application.dtos import CreateHolidayCalendarDTO, HolidayDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import Holiday, HolidayCalendar


class CreateHolidayCalendarUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()

    def execute(self, data: CreateHolidayCalendarDTO) -> HolidayCalendar:
        name = data.name.strip()
        city = data.city.strip()
        uf = data.uf.strip().upper()

        if len(name) == 0:
            raise BadRequestError("Holiday calendar name is required.")
        if len(city) == 0:
            raise BadRequestError("Holiday calendar city is required.")
        if len(uf) == 0:
            raise BadRequestError("Holiday calendar uf is required.")

        self.__validate_holidays(data.holidays)

        existing = self.holiday_calendar_repository.find_by_name(
            tenant_id=data.tenant_id,
            name=name,
        )
        if existing is not None:
            raise ConflictError("Holiday calendar name already exists for this tenant.")

        holiday_calendar = HolidayCalendar(
            tenant_id=data.tenant_id,
            name=name,
            city=city,
            uf=uf,
            holidays=[
                Holiday(
                    holiday_calendar_id=0,
                    date=holiday.date,
                    name=holiday.name.strip(),
                )
                for holiday in data.holidays
            ],
        )
        return self.holiday_calendar_repository.create(holiday_calendar)

    def __validate_holidays(self, holidays: List[HolidayDTO]) -> None:
        used_dates = set()
        for holiday in holidays:
            name = holiday.name.strip()
            if len(name) == 0:
                raise BadRequestError("Holiday name is required.")

            if holiday.date in used_dates:
                raise BadRequestError("Duplicated holiday date in holiday calendar.")

            used_dates.add(holiday.date)
