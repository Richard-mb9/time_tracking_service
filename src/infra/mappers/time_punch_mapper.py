from sqlalchemy import Column, DateTime, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import TimePunch

from . import mapper_registry

time_punch = Table(
    "time_punch",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("employee_id", Integer, nullable=False, index=True),
    Column("matricula", Text, nullable=False, index=True),
    Column("punched_at", DateTime(timezone=True), nullable=False),
    Column("punch_type", Text, nullable=False),
    Column("source", Text, nullable=False),
    Column("note", Text, nullable=True),
)

mapper_registry.map_imperatively(
    TimePunch,
    time_punch,
    properties={
        "adjustment_items": relationship("TimeAdjustmentItem", back_populates="original_punch"),
    },
)
