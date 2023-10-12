from protocol import Protocol
from middleware import Middleware

from ._config import REPLICAS


def stop_consuming(
    filter_name: str,
    data: list[list],
    header: str,
    upstream: Middleware,
    downstream: Middleware,
    result=0,
):
    stopped = int(data[0][0]) + 1
    print(f"{filter_name} | {header} | {stopped}/{REPLICAS}", flush=True)
    if stopped < REPLICAS:
        upstream.send_message(
            Protocol.serialize_msg(header, [[stopped]]),
        )
    else:
        print(f"{filter_name} | sending | EOF", flush=True)
        downstream.send_message(Protocol.serialize_msg(header, [[result]]))
    upstream.close_connection()
