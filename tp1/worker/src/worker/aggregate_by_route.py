from config import Queues
from protocol import Protocol
from middleware import Middleware
from middleware.producer_consumer import ProducerConsumer

from ._utils import stop_consuming, top_2_fastest_by_route
from logs import getLogger

log = getLogger(__name__)

WORKER_TYPE = "aggregate_by_route"


def main():
    upstream = Middleware(ProducerConsumer(Queues.PARTIAL_ROUTE_AGG))
    downstream = Middleware(ProducerConsumer(Queues.TOP_2_FASTESTS_BY_ROUTE))

    def consume(msg: bytes, delivery_tag: int):
        top_2_fastest = {}

        if msg is None:
            log.error(f"no-message")
            upstream.send_nack(delivery_tag)
            return

        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(data, header, upstream, downstream, delivery_tag)
            return

        while data:
            new_flight = data.pop()
            top_2_fastest_by_route(top_2_fastest, new_flight)

        results = [flight for flights in top_2_fastest.values() for flight in flights]
        downstream.send_message(Protocol.serialize_msg("query3", results))
        upstream.send_ack(delivery_tag)
            
    log.hinfo(f"READY")
    upstream.get_message(consume)

    log.hinfo(f"running")
