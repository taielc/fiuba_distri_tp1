from config import Queues
from protocol import Protocol
from middleware import Middleware
from middleware.producer_consumer import ProducerConsumer

from ._utils import stop_consuming, top_2_fastest_by_route

WORKER_TYPE = "top_2_fastest_flights_by_route_acc"


def main():
    upstream = Middleware(ProducerConsumer(Queues.TOP_2_FASTESTS_BY_ROUTE))
    results = Middleware(ProducerConsumer(Queues.RESULTS))

    top_2_fastest = {}

    def consume(msg: bytes, delivery_tag: int):

        if msg is None:
            print(f"{WORKER_TYPE} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(WORKER_TYPE, data, header, upstream, results, "query3")
            acc_results = [flight for flights in top_2_fastest.values() for flight in flights]
            results.send_message(Protocol.serialize_msg(header, acc_results))
            return

        while data:
            new_flight = data.pop()
            top_2_fastest_by_route(top_2_fastest, new_flight)

    print(f"{WORKER_TYPE} | READY", flush=True)
    upstream.get_message(consume)

    print(f"{WORKER_TYPE} | running")
