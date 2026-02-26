from sqlalchemy import Column, Date, Integer, Table, Text

from domain import DailyAttendanceSummary

from . import mapper_registry

daily_attendance_summary = Table(
    "daily_attendance_summary",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("employee_id", Integer, nullable=False, index=True),
    Column("matricula", Text, nullable=False, index=True),
    Column("work_date", Date, nullable=False),
    Column("expected_minutes", Integer, nullable=False),
    Column("worked_minutes", Integer, nullable=False),
    Column("break_minutes", Integer, nullable=False),
    Column("overtime_minutes", Integer, nullable=False),
    Column("deficit_minutes", Integer, nullable=False),
    Column("status", Text, nullable=False),
)
mapper_registry.map_imperatively(DailyAttendanceSummary, daily_attendance_summary)
