from typing import Any, Dict, List, Optional, Tuple

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

        candidate_effective_from = (
            data.effective_from
            if data.effective_from is not None
            else holiday_calendar.effective_from
        )
        candidate_effective_to = (
            data.effective_to
            if data.effective_to is not None
            else holiday_calendar.effective_to
        )
        if candidate_effective_to < candidate_effective_from:
            raise BadRequestError("effective_to must be greater than or equal to effective_from.")

        candidate_national = (
            data.national if data.national is not None else holiday_calendar.national
        )
        normalized_city: Optional[str] = None
        normalized_uf: Optional[str] = None
        if candidate_national is True:
            self.__normalize_location_fields(
                national=True,
                city=data.city,
                uf=data.uf,
            )
        else:
            candidate_city = data.city if data.city is not None else holiday_calendar.city
            candidate_uf = data.uf if data.uf is not None else holiday_calendar.uf
            normalized_city, normalized_uf = self.__normalize_location_fields(
                national=False,
                city=candidate_city,
                uf=candidate_uf,
            )

        if data.effective_from is not None:
            data_to_update["effective_from"] = data.effective_from

        if data.effective_to is not None:
            data_to_update["effective_to"] = data.effective_to

        if data.national is not None:
            data_to_update["national"] = data.national

        if candidate_national is True:
            data_to_update["city"] = None
            data_to_update["uf"] = None
        else:
            if data.city is not None:
                data_to_update["city"] = normalized_city
            if data.uf is not None:
                data_to_update["uf"] = normalized_uf

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
