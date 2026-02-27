from sqlalchemy import Column, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import HolidayCalendar

from . import mapper_registry

holiday_calendar = Table(
    "holiday_calendar",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("name", Text, nullable=False),
    Column("city", Text, nullable=False),
    Column("uf", Text, nullable=False),
)

mapper_registry.map_imperatively(
    HolidayCalendar,
    holiday_calendar,
    properties={
        "holidays": relationship(
            "Holiday",
            back_populates="holiday_calendar",
            cascade="all, delete-orphan",
        ),
        "employee_assignments": relationship(
            "EmployeeHolidayCalendarAssignment",
            back_populates="holiday_calendar",
            cascade="all, delete-orphan",
        ),
    },
)
