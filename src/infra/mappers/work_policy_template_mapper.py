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
    Column("daily_work_minutes", Integer, nullable=False),
    Column("break_minutes", Integer, nullable=False),
)

mapper_registry.map_imperatively(
    WorkPolicyTemplate,
    work_policy_template,
    properties={
        "assignments": relationship(
            "EnrollmentPolicyAssignment",
            back_populates="template",
            cascade="all, delete-orphan",
        ),
    },
)
