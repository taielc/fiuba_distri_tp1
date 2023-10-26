from collections import defaultdict
from config import Queues
from middleware import Middleware, ProducerConsumer, Message
from logs import getLogger

log = getLogger(__name__)


def main():
    upstream = Middleware(ProducerConsumer(Queues.PRICE_BY_ROUTE))
    results = Middleware(ProducerConsumer(Queues.RESULTS))

    stats = {
        "processed": 0,
    }

    routes_stats = defaultdict(lambda: {"max": 0, "sum": 0, "count": 0})

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            log.error("no-message")
            upstream.send_nack(delivery_tag)
            return
        header, data = Message.deserialize_msg(msg)

        if header == "EOF":
            upstream.send_ack(delivery_tag)
            upstream.close_connection()
            return

        assert header == "routes"

        stats["processed"] += len(data)
        for row in data:
            route = (row[0], row[1])
            partial_max = int(row[2])
            partial_price = int(row[3])
            partial_count = int(row[4])
            route_stats = routes_stats[route]
            route_stats["max"] = max(route_stats["max"], partial_max)
            route_stats["sum"] += partial_price
            route_stats["count"] += partial_count

        upstream.send_ack(delivery_tag)

    log.hinfo("READY")
    upstream.get_message(consume)

    final = []
    for route, route_stats in routes_stats.items():
        avg = round(route_stats["sum"] / route_stats["count"] / 100, 2)
        max_ = f"{route_stats['max'] // 100}.{route_stats['max'] % 100}"
        final.append([route[0], route[1], avg, max_])
    results.send_message(Message.serialize_msg("query4", final))
    results.send_message(Message.serialize_msg("EOF", [["query4"]]))
    results.close_connection()

    for stat, value in stats.items():
        log.hinfo(f"{stat} | {value}")
