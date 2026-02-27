from sqlalchemy import Column, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import WorkPolicyTemplate

from . import mapper_registry

work_policy_template = Table(
    "work_policy_template",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("tenant_id", Integer, nullable=False, index=True),
    Column("name", Text, nullable=False),
)

mapper_registry.map_imperatively(
    WorkPolicyTemplate,
    work_policy_template,
    properties={
        "work_day_policies": relationship(
            "WorkDayPolicy",
            back_populates="work_policy_template",
            cascade="all, delete-orphan",
        ),
        "assignments": relationship(
            "EnrollmentPolicyAssignment",
            back_populates="template",
            cascade="all, delete-orphan",
        ),
    },
)
