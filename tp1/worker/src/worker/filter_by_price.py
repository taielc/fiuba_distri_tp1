from collections import defaultdict

from middleware import Middleware, ProducerConsumer, ProducerSubscriber, Message
from config import Queues, Subs, BATCH_SIZE

from ._utils import stop_consuming
from logs import getLogger

log = getLogger(__name__)


def parse_coordinates(lat: str, lon: str):
    lat = float(lat)
    lon = float(lon)
    return (lat, lon)


AIRPORTS_ROW_SIZE = 11
WORKER_NAME = "filter_by_price"

def main():
    flights = Middleware(
        ProducerSubscriber(Subs.FLIGHTS, Queues.FILTER_BY_PRICE)
    )
    avg_price = Middleware(ProducerSubscriber(Subs.AVG_PRICE, exclusive=True))
    downstream = Middleware(ProducerConsumer(Queues.PRICE_BY_ROUTE))

    stats = {
        "processed": 0,
        "countdown": None,
        "sum_price": 0,
        "rows_count": 0,
    }
    routes_prices = defaultdict(list)

    def consume_avg_price(msg: bytes, delivery_tag: int):
        if msg is None:
            avg_price.send_nack(delivery_tag)
            return
        avg_price.send_ack(delivery_tag)

        header, (_, results) = Message.deserialize_msg(msg)
        assert header == "EOF"

        stats["sum_price"] = int(results[0])
        stats["rows_count"] = int(results[1])

        avg_price.close_connection()

    def send_downstream():
        # is in x100
        avg_price_value = stats["sum_price"] / (stats["rows_count"] or 1)
        log.hinfo(f"avg_price_value | {avg_price_value}")

        final = []
        stats["total"] = 0
        for route in routes_prices:
            filtered = [
                price
                for price in routes_prices[route]
                if price > avg_price_value
            ]
            if not filtered:
                continue
            final.append(
                [
                    route[0],
                    route[1],
                    max(filtered),
                    sum(filtered),
                    len(filtered),
                ]
            )
            if len(final) == BATCH_SIZE:
                stats["total"] += len(final)
                downstream.send_message(Message.serialize_msg("routes", final))
                final = []
        if final:
            stats["total"] += len(final)
            downstream.send_message(Message.serialize_msg("routes", final))

        log.hinfo(f"processed | {stats['processed']}")
        log.hinfo(f"total | {stats['total']}")

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            flights.send_nack(delivery_tag)
            return

        header, data = Message.deserialize_msg(msg)

        if header == "EOF":
            log.hinfo("airports | EOF")
            avg_price.get_message(consume_avg_price)
            send_downstream()
            stop_consuming(
                data,
                header,
                flights,
                downstream,
                delivery_tag,
                "query4",
            )
            return

        stats["processed"] += len(data)
        for row in data:
            if row[4] == "":
                continue
            routes_prices[(row[1], row[2])].append(int(row[4]))
        flights.send_ack(delivery_tag)

    log.hinfo("READY")
    flights.get_message(consume)

    downstream.close_connection()
