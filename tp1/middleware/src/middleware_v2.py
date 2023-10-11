import pika
from pika.exchange_type import ExchangeType
from typing import Callable


class MiddlewareV2:
    def __init__(
        self,
        host: str = "middleware",
        port: int = 5672,
    ):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials("admin", "admin"),
            )
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.consumer_tags = {}

    def _wrap_callback(self, callback: Callable):
        def wrapper(
            ch: pika.channel.Channel,
            method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties,
            body: bytes,
        ):
            callback(self, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        return wrapper

    def consume(
        self, queue: str, callback: Callable[["MiddlewareV2", bytes], None]
    ):
        """Create a queue and return its name."""
        method_frame = self.channel.queue_declare(queue=queue, auto_delete=True)
        queue = method_frame.method.queue
        self.consumer_tags[queue] = self.channel.basic_consume(
            queue=queue,
            on_message_callback=self._wrap_callback(callback),
        )
        return queue

    def subscribe(self, topic: str, callback: Callable):
        queue = self.consume("", callback)
        self.channel.exchange_declare(
            exchange=topic,
            exchange_type=ExchangeType.topic,
            passive=True,
        )
        self.channel.queue_bind(exchange=topic, queue=queue)

    def cancel(self, queue: str):
        self.channel.basic_cancel(self.consumer_tags[queue])

    def publish(self, topic: str, message: str):
        self.channel.basic_publish(
            exchange=topic,
            routing_key="",
            body=message,
        )

    def push(self, queue: str, message: str):
        self.channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message,
        )

    def start(self):
        self.channel.start_consuming()
