from config import Queues, Subs
from protocol import Protocol
from middleware import Middleware
from middleware.producer_consumer import ProducerConsumer

from ._utils import stop_consuming, top_2_fastest_by_route

WORKER_TYPE = "partial_route_agg"


def main():
    upstream = Middleware(ProducerConsumer(Queues.PARTIAL_ROUTE_AGG))
    downstream = Middleware(ProducerConsumer(Queues.TOP_2_FASTESTS_BY_ROUTE))

    top_2_fastest = {}

    def consume(msg: bytes, delivery_tag: int):
        filter_name = "top_2_fastest_flights_by_route"

        if msg is None:
            print(f"{filter_name} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(filter_name, data, header, upstream, downstream)
            results = [flight for flights in top_2_fastest.values() for flight in flights]
            downstream.send_message(Protocol.serialize_msg(header, results))
            return

        while data:
            new_flight = data.pop()
            top_2_fastest_by_route(top_2_fastest, new_flight)

    print(f"{WORKER_TYPE} | READY", flush=True)
    upstream.get_message(consume)

    print("top_2_fastest_flights_by_route | running")
