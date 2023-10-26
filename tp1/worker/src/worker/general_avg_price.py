from middleware import Middleware, ProducerSubscriber, Publisher, Message
from config import Queues, Subs
from logs import getLogger

from ._config import REPLICAS

log = getLogger(__name__)


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

    stats = {
        "processed": 0,
        "sum_price": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            upstream.send_nack(delivery_tag)
            return

        header, data = Message.deserialize_msg(msg)

        if header == "EOF":
            log.hinfo("flights | EOF")
            stopped = int(data[0][0]) + 1
            log.hinfo(f"{header} | {stopped}/{REPLICAS}")
            if len(data) == 1:
                results = [stats["sum_price"], stats["processed"]]
            else:
                results = [
                    int(data[1][0]) + stats["sum_price"],
                    int(data[1][1]) + stats["processed"],
                ]
            sum_prices = results[0]
            processed = results[1] or 1
            if stopped < REPLICAS:
                log.hinfo(f"partial | {sum_prices / processed}")
                upstream.send_message(
                    Message.serialize_msg(header, [[stopped], results]),
                )
            else:
                log.hinfo(f"final | {sum_prices / processed}")
                log.hinfo("sending | EOF")
                downstream = Middleware(Publisher(Subs.AVG_PRICE))
                downstream.send_message(
                    Message.serialize_msg(header, [[0], results])
                )
                downstream.close_connection()
            upstream.send_ack(delivery_tag)
            upstream.close_connection()
            return

        stats["processed"] += len(data)
        for row in data:
            stats["sum_price"] += int(row[4] or "0")
        upstream.send_ack(delivery_tag)

    log.hinfo("READY")
    upstream.get_message(consume)

    for stat, value in stats.items():
        log.hinfo(f"{stat} | {value}")
