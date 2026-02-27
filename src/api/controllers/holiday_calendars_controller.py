from typing import List, Optional

from api.schemas import (
    AssignEmployeeHolidayCalendarRequest,
    CreateHolidayCalendarRequest,
    DefaultCreateResponse,
    EmployeeHolidayCalendarAssignmentResponse,
    HolidayCalendarResponse,
    HolidayResponse,
    PaginatedResponse,
    UpdateHolidayCalendarRequest,
)
from application.dtos import (
    AssignEmployeeHolidayCalendarDTO,
    CreateHolidayCalendarDTO,
    HolidayDTO,
    ListHolidayCalendarsDTO,
    UpdateHolidayCalendarDTO,
)
from application.exceptions import BadRequestError
from application.usecases.holiday_calendars import (
    AssignEmployeeHolidayCalendarUseCase,
    CreateHolidayCalendarUseCase,
    DeleteHolidayCalendarUseCase,
    FindEmployeeHolidayCalendarAssignmentByEmployeeIdUseCase,
    FindHolidayCalendarByIdUseCase,
    ListHolidayCalendarsUseCase,
    RemoveEmployeeHolidayCalendarAssignmentUseCase,
    UpdateHolidayCalendarUseCase,
)
from domain import EmployeeHolidayCalendarAssignment, Holiday, HolidayCalendar
from infra.database_manager import DatabaseManagerConnection
from infra.repositories import RepositoryManager


class HolidayCalendarsController:
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.repository_manager = RepositoryManager(db_manager=db_manager)

    def create(self, data: CreateHolidayCalendarRequest) -> DefaultCreateResponse:
        holiday_calendar = CreateHolidayCalendarUseCase(self.repository_manager).execute(
            CreateHolidayCalendarDTO(
                tenant_id=data.tenantId,
                name=data.name,
                city=data.city,
                uf=data.uf.value,
                holidays=[
                    HolidayDTO(
                        date=holiday.date,
                        name=holiday.name,
                    )
                    for holiday in data.holidays
                ],
            )
        )
        return DefaultCreateResponse(id=holiday_calendar.id)

    def find_by_id(self, holiday_calendar_id: int, tenant_id: int) -> HolidayCalendarResponse:
        holiday_calendar = FindHolidayCalendarByIdUseCase(self.repository_manager).execute(
            holiday_calendar_id=holiday_calendar_id,
            raise_if_is_none=True,
        )
        if holiday_calendar.tenant_id != tenant_id:
            raise BadRequestError("Holiday calendar does not belong to tenant.")
        return self.__to_holiday_calendar_response(holiday_calendar)

    def list_all(
        self,
        requester_tenant_id: Optional[int],
        page: int,
        per_page: int,
        name: Optional[str],
        city: Optional[str],
        uf: Optional[str],
    ) -> PaginatedResponse[HolidayCalendarResponse]:
        result = ListHolidayCalendarsUseCase(self.repository_manager).execute(
            ListHolidayCalendarsDTO(
                page=page,
                per_page=per_page,
                tenant_id=requester_tenant_id,
                name=name,
                city=city,
                uf=uf,
            )
        )
        return PaginatedResponse(
            data=[self.__to_holiday_calendar_response(item) for item in result.data],
            count=result.count,
            page=result.page,
        )

    def update(
        self,
        holiday_calendar_id: int,
        tenant_id: int,
        data: UpdateHolidayCalendarRequest,
    ) -> HolidayCalendarResponse:
        holiday_calendar = UpdateHolidayCalendarUseCase(self.repository_manager).execute(
            holiday_calendar_id=holiday_calendar_id,
            tenant_id=tenant_id,
            data=UpdateHolidayCalendarDTO(
                name=data.name,
                city=data.city,
                uf=data.uf.value if data.uf is not None else None,
                holidays=(
                    [
                        HolidayDTO(
                            date=holiday.date,
                            name=holiday.name,
                        )
                        for holiday in data.holidays
                    ]
                    if data.holidays is not None
                    else None
                ),
            ),
        )
        return self.__to_holiday_calendar_response(holiday_calendar)

    def delete(self, holiday_calendar_id: int, tenant_id: int) -> None:
        DeleteHolidayCalendarUseCase(self.repository_manager).execute(
            holiday_calendar_id=holiday_calendar_id,
            tenant_id=tenant_id,
        )

    def assign_employee_holiday_calendar(
        self,
        employee_id: int,
        tenant_id: int,
        data: AssignEmployeeHolidayCalendarRequest,
    ) -> EmployeeHolidayCalendarAssignmentResponse:
        assignment = AssignEmployeeHolidayCalendarUseCase(self.repository_manager).execute(
            AssignEmployeeHolidayCalendarDTO(
                tenant_id=tenant_id,
                employee_id=employee_id,
                holiday_calendar_id=data.holidayCalendarId,
            )
        )
        return self.__to_assignment_response(assignment)

    def find_employee_holiday_calendar_assignment(
        self, employee_id: int, tenant_id: int
    ) -> EmployeeHolidayCalendarAssignmentResponse:
        assignment = FindEmployeeHolidayCalendarAssignmentByEmployeeIdUseCase(
            self.repository_manager
        ).execute(
            employee_id=employee_id,
            tenant_id=tenant_id,
            raise_if_is_none=True,
        )
        return self.__to_assignment_response(assignment)

    def remove_employee_holiday_calendar_assignment(
        self, employee_id: int, tenant_id: int
    ) -> None:
        RemoveEmployeeHolidayCalendarAssignmentUseCase(self.repository_manager).execute(
            employee_id=employee_id,
            tenant_id=tenant_id,
        )

    def __to_holiday_calendar_response(self, item: HolidayCalendar) -> HolidayCalendarResponse:
        return HolidayCalendarResponse(
            id=item.id,
            tenantId=item.tenant_id,
            name=item.name,
            city=item.city,
            uf=item.uf,
            holidays=[
                self.__to_holiday_response(holiday)
                for holiday in self.__sort_holidays(item.holidays)
            ],
        )

    def __to_holiday_response(self, item: Holiday) -> HolidayResponse:
        return HolidayResponse(
            id=item.id,
            date=item.date,
            name=item.name,
        )

    def __sort_holidays(self, data: List[Holiday]) -> List[Holiday]:
        return sorted(data, key=lambda item: item.date)

    def __to_assignment_response(
        self, item: EmployeeHolidayCalendarAssignment
    ) -> EmployeeHolidayCalendarAssignmentResponse:
        return EmployeeHolidayCalendarAssignmentResponse(
            id=item.id,
            employeeId=item.employee_id,
            holidayCalendarId=item.holiday_calendar_id,
        )
