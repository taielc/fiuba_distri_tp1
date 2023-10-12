from config import Queues, Subs
from protocol import Protocol
from middleware import Middleware
from middleware.publisher_consumer import PublisherConsumer
from middleware.publisher_suscriber import PublisherSuscriber

from ._config import REPLICAS


def main():
    subscription = Subs.FLIGHTS
    upstream = Queues.FILTER_BY_STOPS
    downstream = Queues.RESULTS


    upstream = Middleware(PublisherSuscriber(Queues.FILTER_BY_STOPS, Subs.FLIGHTS))
    downstream = Middleware(PublisherConsumer(Queues.RESULTS))

    def consume(msg: bytes):
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stopped = int(data[0][0]) + 1
            print(
                f"filter_by_stops | {header} | {stopped}/{REPLICAS}", flush=True
            )
            if stopped < REPLICAS:
                upstream.send_message(
                    Protocol.serialize_msg(header, [[stopped]]),
                )
            else:
                print("filter_by_stops | sending | EOF", flush=True)
                downstream.send_message(Protocol.serialize_msg(header, [[0]]))
            upstream.close_connection()
            return

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
