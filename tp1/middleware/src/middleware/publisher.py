import pika

from .middleware_type import MiddlewareType
from .constants import RABBITMQ_HOST


class Publisher(MiddlewareType):
    def __init__(self, exchange_name: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="middleware",
                credentials=pika.PlainCredentials("admin", "admin"),
            )
        )
        self.channel = self.connection.channel()

        self._exchange_name = exchange_name
        self.handle_message = None

        self.channel.exchange_declare(
            exchange=self._exchange_name,
            exchange_type="fanout",
            auto_delete=True,
        )

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange=self._exchange_name, routing_key="", body=message
        )

    def get_message(self, _handle_message):
        raise NotImplementedError("Publisher does not consume messages")

    def send_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def send_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag)

    def close_connection(self, delete=False):
        self.channel.stop_consuming()
        if delete:
            self.channel.exchange_delete(self._exchange_name)
        self.connection.close()
