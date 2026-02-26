from typing import Any, Dict

from application.integrations import QueueIntegrationInterface


class QueueIntegration(QueueIntegrationInterface):
    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        _ = topic
        _ = payload
