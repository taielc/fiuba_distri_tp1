from config import Queues, Subs
from protocol import Protocol
from middleware import Middleware
from middleware.publisher_consumer import PublisherConsumer
from middleware.publisher_suscriber import PublisherSuscriber

from ._utils import stop_consuming


def main():
    upstream = Middleware(PublisherSuscriber(Queues.FILTER_BY_STOPS, Subs.FLIGHTS))
    downstream = Middleware(PublisherConsumer(Queues.RESULTS))

    def consume(msg: bytes, delivery_tag: int):
        filter_name = "filter_by_stops"

        if msg is None:
            print(f"{filter_name} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(filter_name, data, header, upstream, downstream)

        if header == "airports":
            print(
                f"filter_by_stops | ignoring | {header} | {len(data)}",
                flush=True,
            )
            return

        removed = 0
        rows_with_stops = []
        while data:
            row = data.pop()
            stops_count = row[6].count("-") + 1
            if not row[6] or stops_count < 1:
                removed += 1
                continue
            rows_with_stops.append(row)

        print(f"filter_by_stops | removed | {removed}", flush=True)
        print(f"filter_by_stops | kept | {len(rows_with_stops)}", flush=True)
        if not rows_with_stops:
            return
        downstream.send_message(Protocol.serialize_msg(header, rows_with_stops))

    upstream.get_message(consume)

    print("filter_by_stops | running")
