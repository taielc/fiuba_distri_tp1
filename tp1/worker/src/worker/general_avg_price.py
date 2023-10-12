from utils import distance
from middleware import Middleware, PublisherConsumer, PublisherSuscriber
from config import Queues, Subs
from protocol import Protocol

from ._config import REPLICAS
from ._utils import stop_consuming


def parse_coordinates(lat: str, lon: str):
    lat = float(lat)
    lon = float(lon)
    return (lat, lon)


AIRPORTS_ROW_SIZE = 11
WORKER_NAME = "general_avg_price"


def main():
    upstream = Middleware(
        PublisherSuscriber(Queues.GENERAL_AVG_PRICE, Subs.FLIGHTS)
    )

    stats = {
        "processed": 0,
        "sum_price": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            upstream.send_nack(delivery_tag)
            return
        upstream.send_ack(delivery_tag)

        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            print(f"{WORKER_NAME} | airports | EOF", flush=True)
            upstream.close_connection()
            return

        stats["processed"] += len(data)
        for row in data:
            stats["sum_price"] += int(row[4] or "0")

    upstream.get_message(consume)

    downstream = Middleware(
        # TODO: doesn't need to declare queue
        PublisherSuscriber(Queues.FILTER_BY_PRICE, Subs.AVG_PRICE)
    )
    downstream.send_message(
        Protocol.serialize_msg(
            "avg_price", [[REPLICAS, stats["sum_price"], stats["processed"]]]
        )
    )

    stats["avg_price"] = round(stats["sum_price"] / stats["processed"] / 100, 2)
    for stat, value in stats.items():
        print(f"{WORKER_NAME} | {stat} |", value, flush=True)
