from config import Queues, Subs, MIN_STOPS_COUNT
from protocol import Protocol
from middleware import Middleware, ProducerConsumer, ProducerSubscriber

from ._utils import stop_consuming

WORKER_TYPE = "filter_by_stops"

def main():
    upstream = Middleware(
        ProducerSubscriber(Subs.FLIGHTS, Queues.FILTER_BY_STOPS)
    )
    downstream = Middleware(ProducerConsumer(Queues.RESULTS))

    stats = {
        "processed": 0,
        "passed": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            print(f"{WORKER_TYPE} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                WORKER_TYPE,
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
        downstream.send_message(Protocol.serialize_msg("query1", final))

    print(f"{WORKER_TYPE} | READY", flush=True)
    upstream.get_message(consume)

    for stat, value in stats.items():
        print(f"{WORKER_TYPE} | {stat}", value, flush=True)
