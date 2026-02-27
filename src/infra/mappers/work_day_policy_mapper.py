from sqlalchemy import Column, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship

from domain import WorkDayPolicy

from . import mapper_registry

work_day_policy = Table(
    "work_day_policy",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "work_policy_template_id",
        Integer,
        ForeignKey("work_policy_template.id"),
        nullable=False,
        index=True,
    ),
    Column("daily_work_minutes", Integer, nullable=False),
    Column("break_minutes", Integer, nullable=False),
    Column("week_day", Text, nullable=False),
)

mapper_registry.map_imperatively(
    WorkDayPolicy,
    work_day_policy,
    properties={
        "work_policy_template": relationship(
            "WorkPolicyTemplate",
            back_populates="work_day_policies",
        ),
    },
)
