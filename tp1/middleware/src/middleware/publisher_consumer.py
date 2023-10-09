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

    def get_message(self) -> [bytes, Callable[[bool], None]]:
        method_frame, header_frame, body = self.channel.basic_get(
            queue=self._queue_name
        )
        if not method_frame:
            sleep(5)
            return None, None

        def post_hook(ack=True):
            if ack:
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            else:
                self.channel.basic_nack(delivery_tag=method_frame.delivery_tag)

        return body, post_hook

    def close_connection(self):
        self.connection.close()
