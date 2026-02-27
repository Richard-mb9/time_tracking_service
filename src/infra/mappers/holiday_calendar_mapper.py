from sqlalchemy import Boolean, Column, Date, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import HolidayCalendar

from . import mapper_registry

holiday_calendar = Table(
    "holiday_calendar",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("name", Text, nullable=False),
    Column("city", Text, nullable=True),
    Column("uf", Text, nullable=True),
    Column("effective_from", Date, nullable=False),
    Column("effective_to", Date, nullable=False),
    Column("national", Boolean, nullable=False, default=False),
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
