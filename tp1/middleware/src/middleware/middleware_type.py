from abc import ABC, abstractmethod
from typing import Callable


class MiddlewareType(ABC):
    @abstractmethod
    def send_message(self, message):
        pass

    @abstractmethod
    def get_message(self) -> [bytes, Callable[[bool], None]]:
        pass

    @abstractmethod
    def close_connection(self):
        pass
