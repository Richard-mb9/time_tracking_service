from application.integrations import IntegrationManagerInterface, QueueIntegrationInterface

from .queue_integration import QueueIntegration


class IntegrationManager(IntegrationManagerInterface):
    def queue_integration(self) -> QueueIntegrationInterface:
        return QueueIntegration()
