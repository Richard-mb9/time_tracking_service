from sqlalchemy import Column, Date, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import DailyAttendanceSummary

from . import mapper_registry

daily_attendance_summary = Table(
    "daily_attendance_summary",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False),
    Column("enrollment_id", Integer, ForeignKey("employee_enrollment.id"), nullable=False),
    Column("work_date", Date, nullable=False),
    Column("expected_minutes", Integer, nullable=False),
    Column("worked_minutes", Integer, nullable=False),
    Column("break_minutes", Integer, nullable=False),
    Column("overtime_minutes", Integer, nullable=False),
    Column("deficit_minutes", Integer, nullable=False),
    Column("status", Text, nullable=False),
)

mapper_registry.map_imperatively(
    DailyAttendanceSummary,
    daily_attendance_summary,
    properties={
        "enrollment": relationship("EmployeeEnrollment", back_populates="daily_summaries"),
    },
)
