from collections import defaultdict
from config import Queues
from protocol import Protocol
from middleware import Middleware, ProducerConsumer


WORKER_TYPE = "price_by_route"


def main():
    upstream = Middleware(ProducerConsumer(Queues.PRICE_BY_ROUTE))
    results = Middleware(ProducerConsumer(Queues.RESULTS))

    stats = {
        "processed": 0,
    }

    routes_stats = defaultdict(lambda: {"max": 0, "sum": 0, "count": 0})

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            print("no-message")
            upstream.send_nack(delivery_tag)
            return
        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
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

    print("READY", flush=True)
    upstream.get_message(consume)

    final = []
    for route, route_stats in routes_stats.items():
        avg = round(route_stats["sum"] / route_stats["count"] / 100, 2)
        max_ = f"{route_stats['max'][:-2]}.{route_stats['max'][-2:]}"
        final.append([route[0], route[1], avg, max_])
    results.send_message(Protocol.serialize_msg("query4", final))
    results.send_message(Protocol.serialize_msg("EOF", [["query4"]]))
    results.close_connection()

    for stat, value in stats.items():
        print(f"{stat} | {value}", flush=True)
