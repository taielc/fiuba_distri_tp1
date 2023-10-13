from protocol import Protocol
from middleware import Middleware

from ._config import REPLICAS


def stop_consuming(
    data: list[list],
    header: str,
    upstream: Middleware,
    downstream: Middleware,
    result: int | str = 0,
):
    stopped = int(data[0][0]) + 1
    print(f"{header} | {stopped}/{REPLICAS}", flush=True)
    if stopped < REPLICAS:
        upstream.send_message(
            Protocol.serialize_msg(header, [[stopped]]),
        )
    else:
        print("sending | EOF", flush=True)
        downstream.send_message(Protocol.serialize_msg(header, [[result]]))
    upstream.close_connection()


def top_2_fastest_by_route(top_2_fastest, new_flight):
    key = (
        new_flight[1].upper(),  # origin
        new_flight[2].upper(),  # destination
    )

    if key not in top_2_fastest or len(top_2_fastest[key]) < 2:
        top_2_fastest[key] = top_2_fastest.get(key, []) + [new_flight]
    else:
        min_flight = min(
            top_2_fastest[key], key=lambda x: x[4]
        )  # index 4: duration
        if min_flight[4] < new_flight[4]:
            top_2_fastest[key].remove(min_flight)
            top_2_fastest[key].append(new_flight)
