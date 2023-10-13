import re
from middleware import Middleware, Publisher, ProducerConsumer
from protocol import Protocol
from config import Queues, Subs

from ._utils import stop_consuming


FLIGHT_ROW_SIZE = 27
WORKER_NAME = "base_filter"


def filter_itinerary(data):
    # [z] id (line number)
    # [0] legId
    # [3] startingAirport
    # [4] destinationAirport
    # [6] travelDuration
    # [12] totalFare
    # [14] totalTravelDistance
    # [19] segmentsArrivalAirportCode: remove last (is startingAirport)
    def parse_duration(duration):
        # PxDTyHzM -> x * 24 * 60 + y * 60 + z
        # PTyHzM -> y * 60 + z
        # PTzM -> z
        # PxDT -> x * 24 * 60
        # PTyH -> y * 60
        patron = re.compile(r'P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?$')

        match = patron.match(duration)

        if match is None:
            print("parsing error | duration |", duration)
            return -1

        days = int(match.group(1) or 0)
        hours = int(match.group(2) or 0)
        minutes = int(match.group(3) or 0)
        return days * 24 * 60 + hours * 60 + minutes

    def filter_row(row):
        return [
            row[0],
            row[3].upper(),
            row[4].upper(),
            parse_duration(row[6]),
            int(float(row[12]) * 100),
            row[14],
            "-".join(row[19].split("||")[:-1]),
        ]

    return [filter_row(row) for row in data if len(row) == FLIGHT_ROW_SIZE]


def main():
    upstream = Middleware(ProducerConsumer(Queues.RAW_FLIGHTS))
    downstream = Middleware(Publisher(Subs.FLIGHTS))

    stats = {
        "invalids": [],
        "processed": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        if msg is None:
            print("no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(
                data,
                header,
                upstream,
                downstream,
            )
            return

        stats["processed"] += len(data)
        stats["invalids"].extend(
            [row for row in data if len(row) != FLIGHT_ROW_SIZE]
        )
        data = filter_itinerary(data)

        downstream.send_message(Protocol.serialize_msg(header, data))

    print("READY", flush=True)
    upstream.get_message(consume)

    for stat, value in stats.items():
        print(f"{stat} | {value}", flush=True)
