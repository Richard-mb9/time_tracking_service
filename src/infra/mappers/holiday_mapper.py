from sqlalchemy import Column, Date, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import Holiday

from . import mapper_registry

holiday = Table(
    "holiday",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "holiday_calendar_id",
        Integer,
        ForeignKey("holiday_calendar.id"),
        nullable=False,
        index=True,
    ),
    Column("date", Date, nullable=False),
    Column("name", Text, nullable=False),
)

mapper_registry.map_imperatively(
    Holiday,
    holiday,
    properties={
        "holiday_calendar": relationship("HolidayCalendar", back_populates="holidays"),
    },
)
