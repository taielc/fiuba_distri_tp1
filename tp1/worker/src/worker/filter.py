import re

from middleware import Middleware
from protocol import Protocol


class Filter:
    def __init__(self, name, upstream: Middleware, downstream: Middleware):
        self.name = name
        self.upstream = upstream
        self.downstream = downstream

    def filter_airport(self, data):
        # [0] Airport Code;
        # [5] Latitude;
        # [6] Longitude;
        return [[row[0], row[5], row[6]] for row in data]

    def filter_itinerary(self, data):
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

    def run(self):
        self.upstream.get_message(self.handle_message)

    def handle_message(self, message, delivery_tag):
        if message is None:
            print(f"{self.name} | no-message")
            self.upstream.send_nack(delivery_tag)
            return

        self.upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(message)
        if header == "EOF":
            print(f"{self.name} | EOF")
            self.upstream.close_connection()
            self.downstream.close_connection()
            return

        print(f"{self.name} | {header} | {data}")

        if header == "airports":
            data = self.filter_airport(data)
        elif header == "itineraries":
            data = self.filter_itinerary(data)

        self.downstream.send_message(Protocol.serialize_msg(header, data))
