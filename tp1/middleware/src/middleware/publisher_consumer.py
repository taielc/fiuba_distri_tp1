import pika
from typing import Callable
from time import sleep  # TEMP

from .middleware_type import MiddlewareType
from .constants import RABBITMQ_HOST


class PublisherConsumer(MiddlewareType):
    def __init__(self, queue_name: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="middleware",
                credentials=pika.PlainCredentials("admin", "admin"),
            )
        )
        self.channel = self.connection.channel()

        self._queue_name = queue_name
        self.handle_message = None

        self.channel.queue_declare(queue=self._queue_name, auto_delete=True)
        self.channel.basic_qos(prefetch_count=1)

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange="", routing_key=self._queue_name, body=message
        )

    def get_message(self, handle_message):
        self.handle_message = handle_message

        def callback(channel, method, properties, body):
            self.handle_message(body, method.delivery_tag)
            print(body)
            print()

        self.channel.basic_consume(queue=self._queue_name, on_message_callback=callback)

        self.channel.start_consuming()

    def send_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def send_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag)

    def close_connection(self):
        self.channel.stop_consuming()
        self.connection.close()
