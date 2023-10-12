from config import Queues, Subs
from protocol import Protocol
from middleware import Middleware
from middleware.publisher_consumer import PublisherConsumer

from ._utils import stop_consuming


def main():
    upstream = Middleware(PublisherConsumer(Queues.TOP_2_FASTEST))
    downstream = Middleware(PublisherConsumer(Queues.RESULTS))

    top_2_fastest = {}

    def consume(msg: bytes, delivery_tag: int):
        filter_name = "top_2_fastest_flights_by_route"

        if msg is None:
            print(f"{filter_name} | no-message")
            upstream.send_nack(delivery_tag)
            return

        upstream.send_ack(delivery_tag)
        header, data = Protocol.deserialize_msg(msg)

        if header == "EOF":
            stop_consuming(filter_name, data, header, upstream, downstream)
            results = [flight for flights in top_2_fastest.values() for flight in flights]
            downstream.send_message(Protocol.serialize_msg(header, results))

        # ELIMINAR CUANDO AEROPUERTOS ESTE APARTE
        if header == "airports":
            print(
                f"filter_by_stops | ignoring | {header} | {len(data)}",
                flush=True,
            )
            return

        while data:
            new_flight = data.pop()
            key = (
                new_flight[3].upper(),  # origin
                new_flight[4].upper()   # destination
            )

            if key not in top_2_fastest or len(top_2_fastest[key]) < 2:
                top_2_fastest[key] = top_2_fastest.get(key, []).append(new_flight)
            else:
                min_flight = min(top_2_fastest[key], key=lambda x: x[4])
                if min_flight[4] < new_flight[4]:    # min_flight[4]: duration
                    top_2_fastest[key].remove(min_flight)
                    top_2_fastest[key].append(new_flight)

    upstream.get_message(consume)

    print("top_2_fastest_flights_by_route | running")
