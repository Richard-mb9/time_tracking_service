from typing import List

from application.repositories import TimeAdjustmentItemRepositoryInterface
from domain import TimeAdjustmentItem
from domain.enums import PunchType
from infra.database_manager import DatabaseManagerConnection


class TimeAdjustmentItemRepository(TimeAdjustmentItemRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create_many(self, items: List[TimeAdjustmentItem]) -> List[TimeAdjustmentItem]:
        self.session.add_all(items)
        self.session.commit()
        for item in items:
            self.session.refresh(item)
        return [self.__normalize_item(item) for item in items]

    def find_by_request_id(self, request_id: int) -> List[TimeAdjustmentItem]:
        items = (
            self.session.query(TimeAdjustmentItem)
            .filter(TimeAdjustmentItem.request_id == request_id)
            .order_by(TimeAdjustmentItem.id.asc())
            .all()
        )
        return [self.__normalize_item(item) for item in items]

    def delete_by_request_id(self, request_id: int) -> None:
        (
            self.session.query(TimeAdjustmentItem)
            .filter(TimeAdjustmentItem.request_id == request_id)
            .delete(synchronize_session=False)
        )
        self.session.commit()

    def __normalize_item(self, item: TimeAdjustmentItem) -> TimeAdjustmentItem:
        if isinstance(item.proposed_punch_type, str):
            item.proposed_punch_type = PunchType(item.proposed_punch_type)
        return item
