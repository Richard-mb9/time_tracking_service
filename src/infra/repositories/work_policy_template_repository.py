from typing import Any, Dict, Optional

from application.repositories import WorkPolicyTemplateRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import WorkPolicyTemplate, WorkWeekDay
from infra.database_manager import DatabaseManagerConnection


class WorkPolicyTemplateRepository(WorkPolicyTemplateRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(self, template: WorkPolicyTemplate) -> WorkPolicyTemplate:
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return self.__normalize_template(template)

    def update(
        self, template_id: int, data: Dict[str, Any]
    ) -> Optional[WorkPolicyTemplate]:
        template = self.find_by_id(template_id)
        if template is None:
            return None

        for key, value in data.items():
            setattr(template, key, value)

        self.session.commit()
        self.session.refresh(template)
        return self.__normalize_template(template)

    def delete(self, template_id: int) -> None:
        template = self.find_by_id(template_id)
        if template is None:
            return
        self.session.delete(template)
        self.session.commit()

    def find_by_id(self, template_id: int) -> Optional[WorkPolicyTemplate]:
        template = (
            self.session.query(WorkPolicyTemplate)
            .filter(WorkPolicyTemplate.id == template_id)
            .first()
        )
        return self.__normalize_template(template) if template is not None else None

    def find_by_name(self, tenant_id: int, name: str) -> Optional[WorkPolicyTemplate]:
        template = (
            self.session.query(WorkPolicyTemplate)
            .filter(WorkPolicyTemplate.tenant_id == tenant_id)
            .filter(WorkPolicyTemplate.name == name)
            .first()
        )
        return self.__normalize_template(template) if template is not None else None

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        name: Optional[str] = None,
    ) -> DBPaginatedResult[WorkPolicyTemplate]:
        query = self.session.query(WorkPolicyTemplate)

        if tenant_id is not None:
            query = query.filter(WorkPolicyTemplate.tenant_id == tenant_id)

        if name is not None:
            query = query.filter(WorkPolicyTemplate.name.ilike(f"%{name}%"))

        total = query.count()
        data = (
            query.order_by(WorkPolicyTemplate.id.asc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(
            data=[self.__normalize_template(item) for item in data],
            total_count=total,
        )

    def __normalize_template(self, template: WorkPolicyTemplate) -> WorkPolicyTemplate:
        for policy in template.work_day_policies:
            if isinstance(policy.week_day, str):
                policy.week_day = WorkWeekDay(policy.week_day)
        return template
