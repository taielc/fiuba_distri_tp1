from middleware import Middleware, ProducerSubscriber, Publisher
from config import Queues, Subs
from protocol import Protocol

from ._config import REPLICAS


def parse_coordinates(lat: str, lon: str):
    lat = float(lat)
    lon = float(lon)
    return (lat, lon)


AIRPORTS_ROW_SIZE = 11
WORKER_NAME = "general_avg_price"


def main():
    upstream = Middleware(
        ProducerSubscriber(Subs.FLIGHTS, Queues.GENERAL_AVG_PRICE)
    )
    downstream = Middleware(Publisher(Subs.AVG_PRICE))

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
            print("flights | EOF", flush=True)
            stopped = int(data[0][0]) + 1
            print(f"{header} | {stopped}/{REPLICAS}", flush=True)
            print(data, flush=True)
            if len(data) == 1:
                results = [stats["sum_price"], stats["processed"]]
            else:
                results = [
                    int(data[1][0]) + stats["sum_price"],
                    int(data[1][1]) + stats["processed"],
                ]
            if stopped < REPLICAS:
                print(f"partial | {results[0] / results[1]}", flush=True)
                upstream.send_message(
                    Protocol.serialize_msg(header, [[stopped], results]),
                )
            else:
                print(f"final | {results[0] / results[1]}", flush=True)
                print("sending | EOF", flush=True)
                downstream.send_message(
                    Protocol.serialize_msg(header, [[0], results])
                )
            upstream.close_connection()
            return

        stats["processed"] += len(data)
        for row in data:
            stats["sum_price"] += int(row[4] or "0")

    print("READY", flush=True)
    upstream.get_message(consume)

    for stat, value in stats.items():
        print(f"{stat} | {value}", flush=True)
