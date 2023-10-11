from config import Queues, Subs
from middleware_v2 import MiddlewareV2
from protocol import Protocol

from ._config import REPLICAS


def main():
    subscription = Subs.FLIGHTS
    upstream = Queues.FILTER_BY_STOPS
    downstream = Queues.RESULTS

    def consume(mid: MiddlewareV2, msg: bytes):
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stopped = int(data[0][0]) + 1
            print(
                f"filter_by_stops | {header} | {stopped}/{REPLICAS}", flush=True
            )
            if stopped < REPLICAS:
                mid.push(
                    subscription,
                    Protocol.serialize_msg(header, [[stopped]]),
                )
            else:
                print(f"filter_by_stops | sending | EOF", flush=True)
                mid.push(downstream, Protocol.serialize_msg(header, [[0]]))
            mid.cancel(upstream)
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
        mid.push(downstream, Protocol.serialize_msg(header, rows_with_stops))

    mid = MiddlewareV2()
    mid.consume(upstream, consume)
    mid.subscribe(subscription, upstream)
    mid.declare(downstream)

    print("filter_by_stops | running")
    mid.start()
    mid.close()
