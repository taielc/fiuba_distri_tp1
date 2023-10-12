from utils import distance
from middleware import Middleware, ProducerConsumer, ProducerSubscriber
from config import DISTANCE_MULTIPLIER, Queues, Subs
from protocol import Protocol

from ._utils import stop_consuming


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
    downstream = Middleware(ProducerConsumer(Queues.RESULTS))

    distances = {}
    airports_coordinates = {}
    invalids = []

    def consume_airports(msg: bytes, delivery_tag: int):
        if msg is None:
            airports.send_nack(delivery_tag)
            return
        airports.send_ack(delivery_tag)

        header, data = Protocol.deserialize_msg(msg)
        # [0] Airport Code;
        # [5] Latitude;
        # [6] Longitude;

        if header == "EOF":
            print("airports | EOF", flush=True)
            airports.close_connection()
            return

        for row in data:
            if len(row) != AIRPORTS_ROW_SIZE:
                invalids.append(row)
                continue
            airports_coordinates[row[0]] = parse_coordinates(row[5], row[6])

    print("READY", flush=True)
    airports.get_message(consume_airports)
    print("airports | invalid |", invalids, flush=True)

    stats = {
        "processed": 0,
        "passed": 0,
        "missing_airport": set(),
    }

    def consume_flights(msg: bytes, delivery_tag: int):
        if msg is None:
            flights.send_nack(delivery_tag)
            return
        flights.send_ack(delivery_tag)

        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                WORKER_NAME,
                data,
                header,
                flights,
                downstream,
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
                final.append([row[0], row[1], row[2], row[5], distances[route]])
        stats["passed"] += len(final)

        if not final:
            return

        downstream.send_message(
            Protocol.serialize_msg("query2", final),
        )

    flights.get_message(consume_flights)

    for stat, value in stats.items():
        print(f"{stat} |", value, flush=True)
