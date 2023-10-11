from abc import ABC, abstractmethod


class MiddlewareType(ABC):
    @abstractmethod
    def send_message(self, message):
        pass

    @abstractmethod
    def get_message(self, handle_message):
        pass

    @abstractmethod
    def send_ack(self, delivery_tag):
        pass

    @abstractmethod
    def send_nack(self, delivery_tag):
        pass

    @abstractmethod
    def close_connection(self):
        pass
