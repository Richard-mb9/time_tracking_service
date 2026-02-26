from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import TimePunch

from . import mapper_registry

time_punch = Table(
    "time_punch",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False),
    Column("enrollment_id", Integer, ForeignKey("employee_enrollment.id"), nullable=False),
    Column("punched_at", DateTime(timezone=True), nullable=False),
    Column("punch_type", Text, nullable=False),
    Column("source", Text, nullable=False),
    Column("note", Text, nullable=True),
)

mapper_registry.map_imperatively(
    TimePunch,
    time_punch,
    properties={
        "enrollment": relationship("EmployeeEnrollment", back_populates="time_punches"),
        "adjustment_items": relationship("TimeAdjustmentItem", back_populates="original_punch"),
    },
)
