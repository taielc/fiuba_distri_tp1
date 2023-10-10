import pika
from typing import Callable
from time import sleep  # TEMP

from .middleware_type import MiddlewareType
from .constants import RABBITMQ_HOST


class PublisherConsumer(MiddlewareType):
    def __init__(self, queue_name: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=pika.PlainCredentials("admin", "admin"),
            )
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)

        self._queue_name = queue_name

        self.channel.queue_declare(queue=self._queue_name, auto_delete=True)

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange="", routing_key=self._queue_name, body=message
        )

    def get_message(self):
        method_frame, _, body = self.channel.basic_get(
            queue=self._queue_name
        )
        if not method_frame:
            return None

        if body is None:
            self.send_nack(method_frame.delivery_tag)

        self.send_ack(method_frame.delivery_tag)
        return body

    def send_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def send_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag)

    def close_connection(self):
        self.connection.close()
