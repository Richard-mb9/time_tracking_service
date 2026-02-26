from datetime import date
from typing import Optional

from application.repositories import DailyAttendanceSummaryRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import DailyAttendanceSummary
from domain.enums import DailyAttendanceStatus
from infra.database_manager import DatabaseManagerConnection


class DailyAttendanceSummaryRepository(DailyAttendanceSummaryRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def upsert(self, summary: DailyAttendanceSummary) -> DailyAttendanceSummary:
        existing = self.find_by_employee_and_matricula_and_date(
            summary.employee_id,
            summary.matricula,
            summary.work_date,
        )

        if existing is None:
            self.session.add(summary)
            self.session.commit()
            self.session.refresh(summary)
            return self.__normalize_summary(summary)

        existing.expected_minutes = summary.expected_minutes
        existing.worked_minutes = summary.worked_minutes
        existing.break_minutes = summary.break_minutes
        existing.overtime_minutes = summary.overtime_minutes
        existing.deficit_minutes = summary.deficit_minutes
        existing.status = summary.status

        self.session.commit()
        self.session.refresh(existing)
        return self.__normalize_summary(existing)

    def find_by_id(self, summary_id: int) -> Optional[DailyAttendanceSummary]:
        summary = (
            self.session.query(DailyAttendanceSummary)
            .filter(DailyAttendanceSummary.id == summary_id)
            .first()
        )
        return self.__normalize_summary(summary) if summary is not None else None

    def find_by_employee_and_matricula_and_date(
        self, employee_id: int, matricula: str, work_date: date
    ) -> Optional[DailyAttendanceSummary]:
        summary = (
            self.session.query(DailyAttendanceSummary)
            .filter(DailyAttendanceSummary.employee_id == employee_id)
            .filter(DailyAttendanceSummary.matricula == matricula)
            .filter(DailyAttendanceSummary.work_date == work_date)
            .first()
        )
        return self.__normalize_summary(summary) if summary is not None else None

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        matricula: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[DailyAttendanceStatus] = None,
    ) -> DBPaginatedResult[DailyAttendanceSummary]:
        query = self.session.query(DailyAttendanceSummary)

        if tenant_id is not None:
            query = query.filter(DailyAttendanceSummary.tenant_id == tenant_id)

        if employee_id is not None:
            query = query.filter(DailyAttendanceSummary.employee_id == employee_id)

        if matricula is not None:
            query = query.filter(DailyAttendanceSummary.matricula == matricula)

        if start_date is not None:
            query = query.filter(DailyAttendanceSummary.work_date >= start_date)

        if end_date is not None:
            query = query.filter(DailyAttendanceSummary.work_date <= end_date)

        if status is not None:
            query = query.filter(DailyAttendanceSummary.status == status)

        total = query.count()
        data = (
            query.order_by(DailyAttendanceSummary.work_date.desc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(
            data=[self.__normalize_summary(summary) for summary in data],
            total_count=total,
        )

    def __normalize_summary(
        self, summary: DailyAttendanceSummary
    ) -> DailyAttendanceSummary:
        if isinstance(summary.status, str):
            summary.status = DailyAttendanceStatus(summary.status)
        return summary
