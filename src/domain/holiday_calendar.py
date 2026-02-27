from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .employee_holiday_calendar_assignment import EmployeeHolidayCalendarAssignment
    from .holiday import Holiday


class HolidayCalendar:
    id: int
    tenant_id: int
    name: str
    city: str
    uf: str
    holidays: List["Holiday"]
    employee_assignments: List["EmployeeHolidayCalendarAssignment"]

    def __init__(
        self,
        tenant_id: int,
        name: str,
        city: str,
        uf: str,
        holidays: Optional[List["Holiday"]] = None,
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.city = city
        self.uf = uf
        self.holidays = holidays or []
        self.employee_assignments = []
