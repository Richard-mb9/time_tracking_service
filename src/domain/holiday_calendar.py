from datetime import date
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .employee_holiday_calendar_assignment import EmployeeHolidayCalendarAssignment
    from .holiday import Holiday


class HolidayCalendar:
    id: int
    tenant_id: int
    name: str
    city: Optional[str]
    uf: Optional[str]
    effective_from: date
    effective_to: date
    national: bool
    holidays: List["Holiday"]
    employee_assignments: List["EmployeeHolidayCalendarAssignment"]

    def __init__(
        self,
        tenant_id: int,
        name: str,
        city: Optional[str],
        uf: Optional[str],
        effective_from: date,
        effective_to: date,
        national: bool = False,
        holidays: Optional[List["Holiday"]] = None,
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.city = city
        self.uf = uf
        self.effective_from = effective_from
        self.effective_to = effective_to
        self.national = national
        self.holidays = holidays or []
        self.employee_assignments = []
