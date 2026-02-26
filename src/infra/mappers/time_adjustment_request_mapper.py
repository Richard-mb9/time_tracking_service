from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import TimeAdjustmentRequest

from . import mapper_registry

time_adjustment_request = Table(
    "time_adjustment_request",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False),
    Column("enrollment_id", Integer, ForeignKey("employee_enrollment.id"), nullable=False),
    Column("request_date", Date, nullable=False),
    Column("type", Text, nullable=False),
    Column("status", Text, nullable=False),
    Column("reason", Text, nullable=False),
    Column("created_by", Integer, nullable=False),
    Column("decided_at", DateTime(timezone=True), nullable=True),
    Column("decided_by", Integer, nullable=True),
    Column("decision_reason", Text, nullable=True),
)

mapper_registry.map_imperatively(
    TimeAdjustmentRequest,
    time_adjustment_request,
    properties={
        "request_type": time_adjustment_request.c.type,
        "requester_user_id": time_adjustment_request.c.created_by,
        "decided_by_user_id": time_adjustment_request.c.decided_by,
        "enrollment": relationship("EmployeeEnrollment", back_populates="adjustment_requests"),
        "items": relationship(
            "TimeAdjustmentItem",
            back_populates="request",
            cascade="all, delete-orphan",
        ),
    },
)
