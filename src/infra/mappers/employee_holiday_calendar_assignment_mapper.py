from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from domain import EmployeeHolidayCalendarAssignment

from . import mapper_registry

employee_holiday_calendar_assignment = Table(
    "employee_holiday_calendar_assignment",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("employee_id", Integer, nullable=False, index=True),
    Column(
        "holiday_calendar_id",
        Integer,
        ForeignKey("holiday_calendar.id"),
        nullable=False,
        index=True,
    ),
)

mapper_registry.map_imperatively(
    EmployeeHolidayCalendarAssignment,
    employee_holiday_calendar_assignment,
    properties={
        "holiday_calendar": relationship(
            "HolidayCalendar",
            back_populates="employee_assignments",
        ),
    },
)
