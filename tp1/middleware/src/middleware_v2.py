import pika
from pika.exchange_type import ExchangeType
from typing import Callable

from config import Queues, Subs


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

    def _declare_queue(self, queue: Queues):
        return self.channel.queue_declare(
            queue=queue.value, auto_delete=True
        ).method.queue
    
    def _declare_exchange(self, exchange: Subs):
        self.channel.exchange_declare(
            exchange=exchange.value,
            exchange_type=ExchangeType.fanout,
        ).method
        return exchange.value

    def declare(self, name: Queues | Subs) -> str:
        if isinstance(name, Queues):
            return self._declare_queue(name)
        elif isinstance(name, Subs):
            return self._declare_exchange(name)
        else:
            raise TypeError(f"Invalid type for name: {type(name)}")

    def consume(
        self,
        queue: Queues,
        callback: Callable[["MiddlewareV2", bytes], None],
    ) -> str:
        """Create a queue and return its name."""
        queue_name = self._declare_queue(queue)
        self.consumer_tags[queue] = self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._wrap_callback(callback),
        )
        return queue

    def subscribe(
        self,
        name: Subs,
        queue: Queues,
    ):
        """Subscribe to a topic, return the queue name."""
        queue_name = queue.value
        exchange_name = self._declare_exchange(name)
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name)
        print(f"middleware | subscribed | {name} | {queue_name}")
        return exchange_name, queue_name

    def cancel(self, name: Queues):
        self.channel.basic_cancel(self.consumer_tags[name.value])

    def push(self, name: Queues | Subs, msg: bytes):
        if isinstance(name, Queues):
            routing_key = name.value
            exchange = ""
        elif isinstance(name, Subs):
            exchange = name.value
            routing_key = ""
        else:
            raise TypeError(f"Invalid type for name: {type(name)}")
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=msg,
        )

    def start(self):
        print("middleware | starting", flush=True)
        self.channel.start_consuming()

    def close(self):
        self.channel.stop_consuming()
        self.connection.close()
