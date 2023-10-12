from utils import distance
from middleware import Middleware, PublisherConsumer, PublisherSuscriber
from config import Queues, Subs
from protocol import Protocol
from collections import defaultdict

from ._config import REPLICAS
from ._utils import stop_consuming


def parse_coordinates(lat: str, lon: str):
    lat = float(lat)
    lon = float(lon)
    return (lat, lon)


AIRPORTS_ROW_SIZE = 11
WORKER_NAME = "filter_by_price"


def main():
    flights = Middleware(
        PublisherSuscriber(Queues.FILTER_BY_PRICE, Subs.FLIGHTS)
    )

    stats = {
        "processed": 0,
        "countdown": None,
        "sum_price": 0,
        "rows_count": 0,
    }
    routes_prices = defaultdict(list)

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            flights.send_nack(delivery_tag)
            return
        flights.send_ack(delivery_tag)

        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            print(f"{WORKER_NAME} | airports | EOF", flush=True)
            flights.close_connection()
            return

        stats["processed"] += len(data)
        for row in data:
            if row[4] == "":
                continue
            routes_prices[(row[0], row[1])].append(int(row[4]))

    flights.get_message(consume)
    print(f"{WORKER_NAME} | processed |", stats["processed"], flush=True)

    avg_price = Middleware(
        # TODO: exclusive queue
        PublisherSuscriber(Queues.FILTER_BY_PRICE, Subs.AVG_PRICE)
    )
    downstream = Middleware(PublisherConsumer(Queues.RESULTS))

    def consume_avg_price(msg: bytes, delivery_tag: int):
        if msg is None:
            avg_price.send_nack(delivery_tag)
            return
        avg_price.send_ack(delivery_tag)

        header, data = Protocol.deserialize_msg(msg)
        assert header == "avg_price"

        replicas, partial_sum_price, partial_rows_count = data[0]

        if stats["countdown"] is None:
            stats["countdown"] = int(replicas)
        stats["countdown"] -= 1

        stats["sum_price"] += int(partial_sum_price)
        stats["rows_count"] += int(partial_rows_count)

        if stats["countdown"] == 0:
            avg_price.close_connection()

    avg_price.get_message(consume_avg_price)

    avg_price_value = stats["sum_price"] / stats["rows_count"]
    # is in x100

    final = []
    for route in routes_prices:
        filtered = [
            price for price in routes_prices[route] if price > avg_price_value
        ]
        if not filtered:
            continue
        final.append(
            [
                route[0],
                route[1],
                max(filtered),
                round(sum(filtered) / len(filtered) / 100, 2),
            ]
        )

    downstream.send_message(Protocol.serialize_msg("query4", final))
    downstream.send_message(Protocol.serialize_msg("EOF", [["query4"]]))
