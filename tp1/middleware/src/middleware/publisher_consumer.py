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
        self.delivery_tag = None

        self.channel.queue_declare(queue=self._queue_name, auto_delete=True)

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange="", routing_key=self._queue_name, body=message
        )

    def get_message(self) -> None:
        self.channel.basic_consume(queue=self._queue_name, on_message_callback=callback)

        self.channel.start_consuming()

        def callback(ch, method, properties, body):
            self.delivery_tag = method.delivery_tag
            print(f" [x] Received {body}")
            return body

    def send_ack(self):
        self.channel.basic_ack(delivery_tag=self.delivery_tag)

    def send_nack(self):
        self.channel.basic_nack(delivery_tag=self.delivery_tag)

    def close_connection(self):
        self.connection.close()
