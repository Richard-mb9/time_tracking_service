from sqlalchemy import Boolean, Column, Date, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import EmployeeEnrollment

from . import mapper_registry

employee_enrollment = Table(
    "employee_enrollment",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("employee_id", Integer, nullable=False, index=True),
    Column("matricula", Text, nullable=False),
    Column("active_from", Date, nullable=False),
    Column("active_to", Date, nullable=True),
    Column("is_active", Boolean, nullable=False),
)

mapper_registry.map_imperatively(
    EmployeeEnrollment,
    employee_enrollment,
    properties={
        "enrollment_code": employee_enrollment.c.matricula,
        "policy_assignments": relationship(
            "EnrollmentPolicyAssignment",
            back_populates="enrollment",
            cascade="all, delete-orphan",
        ),
        "time_punches": relationship(
            "TimePunch",
            back_populates="enrollment",
            cascade="all, delete-orphan",
        ),
        "adjustment_requests": relationship(
            "TimeAdjustmentRequest",
            back_populates="enrollment",
            cascade="all, delete-orphan",
        ),
        "daily_summaries": relationship(
            "DailyAttendanceSummary",
            back_populates="enrollment",
            cascade="all, delete-orphan",
        ),
        "bank_hours_entries": relationship(
            "BankHoursLedger",
            back_populates="enrollment",
            cascade="all, delete-orphan",
        ),
    },
)
