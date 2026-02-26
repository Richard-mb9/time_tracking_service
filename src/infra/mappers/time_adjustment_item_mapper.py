from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import TimeAdjustmentItem

from . import mapper_registry

time_adjustment_item = Table(
    "time_adjustment_item",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False),
    Column("request_id", Integer, ForeignKey("time_adjustment_request.id"), nullable=False),
    Column("proposed_punch_type", Text, nullable=True),
    Column("proposed_punched_at", DateTime(timezone=True), nullable=True),
    Column("original_punch_id", Integer, ForeignKey("time_punch.id"), nullable=True),
    Column("note", Text, nullable=True),
)

mapper_registry.map_imperatively(
    TimeAdjustmentItem,
    time_adjustment_item,
    properties={
        "request": relationship("TimeAdjustmentRequest", back_populates="items"),
        "original_punch": relationship("TimePunch", back_populates="adjustment_items"),
    },
)
