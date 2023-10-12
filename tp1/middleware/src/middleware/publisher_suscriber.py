import pika

from .middleware_type import MiddlewareType
from .constants import RABBITMQ_HOST


class PublisherSuscriber(MiddlewareType):
    def __init__(self, queue_name: str, exchange_name: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="middleware",
                credentials=pika.PlainCredentials("admin", "admin"),
            )
        )
        self.channel = self.connection.channel()

        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self.handle_message = None

        self.channel.exchange_declare(
            exchange=self._exchange_name, exchange_type="fanout"
        )

        self.channel.basic_qos(prefetch_count=1)

        self.channel.queue_declare(queue=self._queue_name, auto_delete=True)

        self.channel.queue_bind(
            exchange=self._exchange_name, queue=self._queue_name
        )

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange=self._exchange_name, routing_key="", body=message
        )

    def get_message(self, handle_message):
        self.handle_message = handle_message

        def callback(channel, method, properties, body):
            self.handle_message(body, method.delivery_tag)

        self.channel.basic_consume(
            queue=self._queue_name, on_message_callback=callback
        )

        self.channel.start_consuming()

    def send_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def send_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag)

    def close_connection(self):
        self.channel.stop_consuming()
        self.channel.exchange_delete(self._exchange_name)
        self.connection.close()
