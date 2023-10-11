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
        self.handle_message = None

        self.channel.queue_declare(queue=self._queue_name, auto_delete=True)

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange="", routing_key=self._queue_name, body=message
        )

    def get_message(self, handle_message):
        self.handle_message = handle_message

        def callback(channel, method, properties, body):
            # self.handle_message(body, method.delivery_tag)
            print(body)
            print()
            channel.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=self._queue_name, on_message_callback=callback, auto_ack=False)

        self.channel.start_consuming()

    def send_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def send_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag)

    def close_connection(self):
        self.connection.close()
