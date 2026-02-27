from typing import List, Optional, Tuple

from application.dtos import CreateHolidayCalendarDTO, HolidayDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import Holiday, HolidayCalendar


class CreateHolidayCalendarUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()

    def execute(self, data: CreateHolidayCalendarDTO) -> HolidayCalendar:
        name = data.name.strip()

        if len(name) == 0:
            raise BadRequestError("Holiday calendar name is required.")
        if data.effective_to < data.effective_from:
            raise BadRequestError("effective_to must be greater than or equal to effective_from.")

        city, uf = self.__normalize_location_fields(
            national=data.national,
            city=data.city,
            uf=data.uf,
        )

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
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            national=data.national,
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

    def __normalize_location_fields(
        self,
        national: bool,
        city: Optional[str],
        uf: Optional[str],
    ) -> Tuple[Optional[str], Optional[str]]:
        normalized_city = city.strip() if city is not None else None
        normalized_uf = uf.strip().upper() if uf is not None else None

        if national is True:
            if city is not None or uf is not None:
                raise BadRequestError("city and uf must be null when national is true.")
            return None, None

        if normalized_city is None or len(normalized_city) == 0:
            raise BadRequestError("Holiday calendar city is required when national is false.")
        if normalized_uf is None or len(normalized_uf) == 0:
            raise BadRequestError("Holiday calendar uf is required when national is false.")
        return normalized_city, normalized_uf
