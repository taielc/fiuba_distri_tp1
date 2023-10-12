from protocol import Protocol


def stop_consuming(filter_name, replicas, data, header, upstream, downstream):
    stopped = int(data[0][0]) + 1
    print(f"{filter_name} | {header} | {stopped}/{REPLICAS}", flush=True)
    if stopped < replicas:
        upstream.send_message(
            Protocol.serialize_msg(header, [[stopped]]),
        )
    else:
        print(f"{filter_name} | sending | EOF", flush=True)
        downstream.send_message(Protocol.serialize_msg(header, [[0]]))
    upstream.close_connection()
