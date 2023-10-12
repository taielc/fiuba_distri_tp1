from protocol import Protocol
from config import Queues, Subs
import re
from middleware import Middleware, PublisherConsumer, PublisherSuscriber


from ._config import REPLICAS


def filter_airport(data):
    # [0] Airport Code;
    # [5] Latitude;
    # [6] Longitude;
    return [[row[0], row[5], row[6]] for row in data]


def filter_itinerary(data):
    # [0] legId
    # [3] startingAirport
    # [4] destinationAirport
    # [6] travelDuration
    # [12] totalFare
    # [14] totalTravelDistance
    # [19] segmentsArrivalAirportCode: remove last (is startingAirport)
    def parse_duration(duration):
        # PTxHyM -> x * 60 + y
        match = re.match(r"PT(\d+)H(\d+)M", duration)
        if match is None:
            print("filter | parsing error | duration |", duration)
            return -1
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 60 + minutes

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

    return [filter_row(row) for row in data]


def main():
    upstream = Middleware(PublisherConsumer(Queues.FLIGHTS_RAW))
    downstream = Middleware(
        PublisherSuscriber(Queues.FILTER_BY_STOPS, Subs.FLIGHTS)
    )

    def consume(msg: bytes):
        header, data = Protocol.deserialize_msg(msg)

        shape = (len(data), len(data[0]))
        print(f"base_filter | received | {header} | {shape}")
        if header == "EOF":
            stopped = int(data[0][0]) + 1
            print(f"base_filter | {header} | {stopped}/{REPLICAS}")
            if stopped < REPLICAS:
                upstream.send_message(
                    Protocol.serialize_msg(header, [[stopped]]),
                )
            else:
                downstream.send_message(Protocol.serialize_msg(header, [[0]]))
            upstream.close_connection()
            return

        if header == "airports":
            data = filter_airport(data)
        elif header == "itineraries":
            data = filter_itinerary(data)

        downstream.send_message(Protocol.serialize_msg(header, data))

    upstream.get_message(consume)
