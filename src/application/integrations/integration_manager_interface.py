from abc import ABC, abstractmethod

from .queue_integration_interface import QueueIntegrationInterface


class IntegrationManagerInterface(ABC):
    @abstractmethod
    def queue_integration(self) -> QueueIntegrationInterface:
        raise NotImplementedError
