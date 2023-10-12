from config import Queues, Subs, MIN_STOPS_COUNT
from protocol import Protocol
from middleware import Middleware
from middleware.publisher_consumer import PublisherConsumer
from middleware.publisher_suscriber import PublisherSuscriber

from ._utils import stop_consuming


def main():
    upstream = Middleware(
        PublisherSuscriber(Queues.FILTER_BY_STOPS, Subs.FLIGHTS)
    )
    downstream = Middleware(PublisherConsumer(Queues.RESULTS))

    stats = {
        "processed": 0,
        "passed": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        filter_name = "filter_by_stops"

        if msg is None:
            print(f"{filter_name} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                filter_name,
                data,
                header,
                upstream,
                downstream,
                result="query1",
            )
            return

        stats["processed"] += len(data)
        final = []
        while data:
            row = data.pop()
            stops_count = row[6].count("-") + 1
            if not row[6] or stops_count < MIN_STOPS_COUNT:
                continue
            final.append(
                [row[0], row[1], row[2], f"{row[4][:-2]}.{row[4][-2:]}"]
            )
        stats["passed"] += len(final)

        if not final:
            return
        downstream.send_message(Protocol.serialize_msg(header, final))

    upstream.get_message(consume)

    for stat, value in stats.items():
        print(f"filter_by_stops | {stat}", value, flush=True)
