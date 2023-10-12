import re
from middleware import Middleware, PublisherConsumer, PublisherSuscriber
from protocol import Protocol
from config import Queues, Subs

from ._utils import stop_consuming


FLIGHT_ROW_SIZE = 27


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
        match = re.match(
            r"P((?P<days>\d+)DT)?((?P<hours>\d+)H)?((?P<minutes>\d+)M)?",
            duration,
        )
        if match is None:
            print("filter | parsing error | duration |", duration)
            return -1
        groups = match.groupdict("0")
        days = int(groups["days"])
        hours = int(groups["hours"])
        minutes = int(groups["minutes"])
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
    upstream = Middleware(PublisherConsumer(Queues.RAW_FLIGHTS))
    downstream = Middleware(
        PublisherSuscriber(Queues.DIST_CALCULATION, Subs.FLIGHTS)
    )

    stats = {
        "invalids": [],
        "processed": 0,
    }

    def consume(msg: bytes, delivery_tag: int):
        filter_name = "base_filter"

        if msg is None:
            print(f"{filter_name} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(filter_name, data, header, upstream, downstream)
            return

        stats["processed"] += len(data)
        stats["invalids"].extend(
            [row for row in data if len(row) != FLIGHT_ROW_SIZE]
        )
        data = filter_itinerary(data)

        downstream.send_message(Protocol.serialize_msg(header, data))

    upstream.get_message(consume)

    for stat, value in stats.items():
        print(f"base_filter | {stat}", value, flush=True)
