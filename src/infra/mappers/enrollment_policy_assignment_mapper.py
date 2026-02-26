from sqlalchemy import Column, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from domain import EnrollmentPolicyAssignment

from . import mapper_registry

enrollment_policy_assignment = Table(
    "enrollment_policy_assignment",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False),
    Column("enrollment_id", Integer, ForeignKey("employee_enrollment.id"), nullable=False),
    Column("template_id", Integer, ForeignKey("work_policy_template.id"), nullable=False),
    Column("effective_from", Date, nullable=False),
    Column("effective_to", Date, nullable=True),
)

mapper_registry.map_imperatively(
    EnrollmentPolicyAssignment,
    enrollment_policy_assignment,
    properties={
        "enrollment": relationship("EmployeeEnrollment", back_populates="policy_assignments"),
        "template": relationship("WorkPolicyTemplate", back_populates="assignments"),
    },
)
