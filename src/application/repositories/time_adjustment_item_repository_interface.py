from abc import ABC, abstractmethod
from typing import List

from domain import TimeAdjustmentItem


class TimeAdjustmentItemRepositoryInterface(ABC):
    @abstractmethod
    def create_many(self, items: List[TimeAdjustmentItem]) -> List[TimeAdjustmentItem]:
        raise NotImplementedError

    @abstractmethod
    def find_by_request_id(self, request_id: int) -> List[TimeAdjustmentItem]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_request_id(self, request_id: int) -> None:
        raise NotImplementedError
