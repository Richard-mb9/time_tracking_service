from abc import ABC, abstractmethod
from typing import Any, Dict


class QueueIntegrationInterface(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        raise NotImplementedError
