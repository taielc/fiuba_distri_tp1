from middleware_type import MiddlewareType
from constants import RABBITMQ_HOST
import pika


class PublisherConsumer(MiddlewareType):

    def __init__(self, queue_name: str):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.channel = self.connection.channel()

        self._queue_name = queue_name

        self.channel.queue_declare(queue=self._queue_name)

    def send_message(self, message: str):
        print(f"sending message: {message}")
        self.channel.basic_publish(exchange='', routing_key=self._queue_name, body=message)

    def close_connection(self):
        self.connection.close()
