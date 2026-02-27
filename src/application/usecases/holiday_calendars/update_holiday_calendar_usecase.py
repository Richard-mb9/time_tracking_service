from typing import Any, Dict, List

from application.dtos import HolidayDTO, UpdateHolidayCalendarDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import Holiday, HolidayCalendar

from .find_holiday_calendar_by_id_usecase import FindHolidayCalendarByIdUseCase


class UpdateHolidayCalendarUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.holiday_calendar_repository = repository_manager.holiday_calendar_repository()
        self.find_by_id_usecase = FindHolidayCalendarByIdUseCase(repository_manager)

    def execute(
        self,
        holiday_calendar_id: int,
        tenant_id: int,
        data: UpdateHolidayCalendarDTO,
    ) -> HolidayCalendar:
        holiday_calendar = self.find_by_id_usecase.execute(
            holiday_calendar_id=holiday_calendar_id,
            raise_if_is_none=True,
        )
        if holiday_calendar.tenant_id != tenant_id:
            raise BadRequestError("Holiday calendar does not belong to tenant.")

        data_to_update: Dict[str, Any] = {}

        if data.name is not None:
            name = data.name.strip()
            if len(name) == 0:
                raise BadRequestError("Holiday calendar name is required.")
            existing = self.holiday_calendar_repository.find_by_name(
                tenant_id=tenant_id,
                name=name,
            )
            if existing is not None and existing.id != holiday_calendar.id:
                raise ConflictError("Holiday calendar name already exists for this tenant.")
            data_to_update["name"] = name

        if data.city is not None:
            city = data.city.strip()
            if len(city) == 0:
                raise BadRequestError("Holiday calendar city is required.")
            data_to_update["city"] = city

        if data.uf is not None:
            uf = data.uf.strip().upper()
            if len(uf) == 0:
                raise BadRequestError("Holiday calendar uf is required.")
            data_to_update["uf"] = uf

        if data.holidays is not None:
            self.__validate_holidays(data.holidays)
            data_to_update["holidays"] = [
                Holiday(
                    holiday_calendar_id=holiday_calendar.id,
                    date=holiday.date,
                    name=holiday.name.strip(),
                )
                for holiday in data.holidays
            ]

        if len(data_to_update) == 0:
            return holiday_calendar

        updated = self.holiday_calendar_repository.update(
            holiday_calendar_id=holiday_calendar_id,
            data=data_to_update,
        )
        if updated is None:
            raise BadRequestError("Unable to update holiday calendar.")
        return updated

    def __validate_holidays(self, holidays: List[HolidayDTO]) -> None:
        used_dates = set()
        for holiday in holidays:
            name = holiday.name.strip()
            if len(name) == 0:
                raise BadRequestError("Holiday name is required.")

            if holiday.date in used_dates:
                raise BadRequestError("Duplicated holiday date in holiday calendar.")

            used_dates.add(holiday.date)
