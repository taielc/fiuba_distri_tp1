import pika

from config import MIDDLEWARE_HOST, MIDDLEWARE_HEARTBEAT
from logs import getLogger

from .middleware_type import MiddlewareType


log = getLogger(__name__)


class ProducerSubscriber(MiddlewareType):
    def __init__(
        self, exchange_name: str, queue_name: str = None, exclusive=False
    ):
        assert (queue_name or exclusive) and not (
            queue_name and exclusive
        ), "You must specify either a queue name or set exclusive to True"
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=MIDDLEWARE_HOST,
                credentials=pika.PlainCredentials("admin", "admin"),
                heartbeat=MIDDLEWARE_HEARTBEAT,
            )
        )
        self.channel = self.connection.channel()

        self._exchange_name = exchange_name
        self.handle_message = None

        self.channel.exchange_declare(
            exchange=self._exchange_name,
            exchange_type="fanout",
            auto_delete=False,
        )
        self.channel.basic_qos(prefetch_count=1)

        self._exclusive = exclusive
        # get the queue name from declaration
        self._queue_name = self.channel.queue_declare(
            queue="" if exclusive else queue_name,
            auto_delete=exclusive,
            exclusive=exclusive,
        ).method.queue

        self.channel.queue_bind(
            exchange=self._exchange_name, queue=self._queue_name
        )

    def _reconnect(self):
        # self.close_connection()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=MIDDLEWARE_HOST,
                credentials=pika.PlainCredentials("admin", "admin"),
            )
        )
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_declare(
            queue=self._queue_name,
            auto_delete=self._exclusive,
            exclusive=self._exclusive,
        )

        self.channel.queue_bind(
            exchange=self._exchange_name, queue=self._queue_name
        )

        def callback(channel, method, properties, body):
            self.handle_message(body, method.delivery_tag)

        self.channel.basic_consume(
            queue=self._queue_name, on_message_callback=callback
        )

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange="", routing_key=self._queue_name, body=message
        )

    def get_message(self, handle_message):
        self.handle_message = handle_message

        def callback(channel, method, properties, body):
            self.handle_message(body, method.delivery_tag)

        self.channel.basic_consume(
            queue=self._queue_name, on_message_callback=callback
        )

        # while not self.connection.is_closed:
        #     try:
        self.channel.start_consuming()
            # except pika.exceptions.StreamLostError:
            #     log.warning("Stream lost, reconnecting...")
            #     self.send_nack()
            #     self._reconnect()

    def send_ack(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def send_nack(self, delivery_tag):
        self.channel.basic_nack(delivery_tag=delivery_tag)

    def close_connection(self, delete=False):
        self.channel.stop_consuming()
        if self._exclusive:
            self.channel.queue_delete(self._queue_name)
        if delete:
            self.channel.exchange_delete(self._exchange_name)
        self.connection.close()
