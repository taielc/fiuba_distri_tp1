from config import Queues
from middleware import Middleware, Message
from middleware.producer_consumer import ProducerConsumer
from logs import getLogger

from ._utils import stop_consuming, top_2_fastest_by_route

log = getLogger(__name__)


def main():
    upstream = Middleware(ProducerConsumer(Queues.TOP_2_FASTESTS_BY_ROUTE))
    results = Middleware(ProducerConsumer(Queues.RESULTS))

    def consume(msg: bytes, delivery_tag: int):
        top_2_fastest = {}

        if msg is None:
            log.error("no-message")
            upstream.send_nack(delivery_tag)
            return

        header, data = Message.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                data,
                header,
                upstream,
                results,
                delivery_tag,
                result="query3",)
            return

        while data:
            new_flight = data.pop()
            top_2_fastest_by_route(top_2_fastest, new_flight)
        
        acc_results = [flight for flights in top_2_fastest.values() for flight in flights]
        results.send_message(Message.serialize_msg("query3", acc_results))
        upstream.send_ack(delivery_tag)

    log.hinfo("READY")
    upstream.get_message(consume)
