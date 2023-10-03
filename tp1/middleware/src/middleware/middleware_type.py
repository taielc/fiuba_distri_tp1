from abc import ABC, abstractmethod


class MiddlewareType(ABC):

    @abstractmethod
    def send_message(self, message):
        pass
