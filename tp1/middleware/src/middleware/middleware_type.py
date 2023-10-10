from abc import ABC, abstractmethod


class MiddlewareType(ABC):
    @abstractmethod
    def send_message(self, message):
        pass

    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def send_ack(self):
        pass

    @abstractmethod
    def send_nack(self):
        pass

    @abstractmethod
    def close_connection(self):
        pass
