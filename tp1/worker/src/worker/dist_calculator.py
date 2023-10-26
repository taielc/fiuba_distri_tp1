from utils import distance
from middleware import Middleware, ProducerConsumer, ProducerSubscriber, Message
from config import DISTANCE_MULTIPLIER, Queues, Subs
from logs import getLogger

from ._utils import stop_consuming

log = getLogger(__name__)


def parse_coordinates(lat: str, lon: str):
    lat = float(lat)
    lon = float(lon)
    return (lat, lon)


AIRPORTS_ROW_SIZE = 11
WORKER_NAME = "dist_calculator"


def main():
    airports = Middleware(ProducerSubscriber(Subs.AIRPORTS, exclusive=True))
    flights = Middleware(
        ProducerSubscriber(Subs.FLIGHTS, Queues.DIST_CALCULATION)
    )
    results = Middleware(ProducerConsumer(Queues.RESULTS))

    distances = {}
    airports_coordinates = {}
    invalids = []

    def consume_airports(msg: bytes, delivery_tag: int):
        if msg is None:
            airports.send_nack(delivery_tag)
            return

        header, data = Message.deserialize_msg(msg)
        # [0] Airport Code;
        # [5] Latitude;
        # [6] Longitude;

        if header == "EOF":
            log.hinfo("airports | EOF")
            airports.send_ack(delivery_tag)
            airports.close_connection()
            return

        for row in data:
            if len(row) != AIRPORTS_ROW_SIZE:
                invalids.append(row)
                continue
            airports_coordinates[row[0]] = parse_coordinates(row[5], row[6])
        
        airports.send_ack(delivery_tag)

    log.hinfo("READY")
    airports.get_message(consume_airports)
    if invalids:
        log.warning(f"airports | invalid | {invalids}")

    stats = {
        "processed": 0,
        "passed": 0,
        "missing_airport": set(),
    }

    def consume_flights(msg: bytes, delivery_tag: int):
        if msg is None:
            flights.send_nack(delivery_tag)
            return

        header, data = Message.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                data,
                header,
                flights,
                results,
                delivery_tag,
                "query2",
            )
            return

        stats["processed"] += len(data)
        final = []
        for row in data:
            route = (row[1], row[2])
            if route not in distances:
                if route[0] not in airports_coordinates:
                    stats["missing_airport"].add(route[0])
                    continue
                if route[1] not in airports_coordinates:
                    stats["missing_airport"].add(route[1])
                    continue
                distances[route] = distance(
                    airports_coordinates[route[0]],
                    airports_coordinates[route[1]],
                )

            if distances[route] * DISTANCE_MULTIPLIER < int(row[5] or "0"):
                final.append([row[0], row[1], row[2], row[5]])
        stats["passed"] += len(final)

        if final:
            results.send_message(
                Message.serialize_msg("query2", final),
            )
        flights.send_ack(delivery_tag)

    flights.get_message(consume_flights)

    for stat, value in stats.items():
        log.hdebug(f"{stat} | {value}")
