from config import Queues, Subs, MIN_STOPS_COUNT
from protocol import Protocol
from middleware import Middleware, ProducerConsumer, ProducerSubscriber

from ._utils import stop_consuming
from ._config import REPLICAS
from logs import getLogger

log = getLogger(__name__)

WORKER_TYPE = "filter_by_stops"


def main():
    downstream = Middleware(ProducerConsumer(Queues.PARTIAL_ROUTE_AGG))
    upstream = Middleware(
        ProducerSubscriber(Subs.FLIGHTS, Queues.FILTER_BY_STOPS)
    )

    results = Middleware(ProducerConsumer(Queues.RESULTS))

    stats = {
        "processed": 0,
        "passed": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            log.error("no-message")
            upstream.send_nack(delivery_tag)
            return
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                data,
                header,
                upstream,
                results,
                delivery_tag,
                result="query1",
            )

            stopped = int(data[0][0]) + 1
            log.hinfo(
                f"{header} | {stopped}/{REPLICAS}"
            )
            if stopped == REPLICAS:
                log.hinfo(f"sending | EOF")
                downstream.send_message(
                    Protocol.serialize_msg(header, [["0"], [REPLICAS]])
                )

            return

        stats["processed"] += len(data)
        filtered = []
        while data:
            row = data.pop()
            stops_count = row[6].count("-") + 1
            if not row[6] or stops_count < MIN_STOPS_COUNT:
                continue
            filtered.append(row)
        stats["passed"] += len(filtered)

        if not filtered:
            upstream.send_ack(delivery_tag)
            return

        filtered_q3 = [
            [row[0], row[1], row[2], row[6], int(row[3])] for row in filtered
        ]

        filtered_q1 = [
            [row[0], row[1], row[2], f"{row[4][:-2]}.{row[4][-2:]}", row[6]]
            for row in filtered
        ]

        downstream.send_message(Protocol.serialize_msg(header, filtered_q3))
        results.send_message(Protocol.serialize_msg("query1", filtered_q1))
        upstream.send_ack(delivery_tag)

    log.hinfo("READY")
    upstream.get_message(consume)

    for stat, value in stats.items():
        log.hinfo(f"{stat} | {value}")
