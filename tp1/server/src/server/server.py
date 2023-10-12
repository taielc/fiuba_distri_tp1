from logging import getLogger

from config import SERVER_PORT, Queues, Subs
from middleware import Middleware, ProducerConsumer, Publisher
from protocol import Protocol
from tcp import ServerSocket, Socket

log = getLogger(__name__)


class Server:
    def __init__(self, port: int = SERVER_PORT):
        self.port = port
        self.socket = ServerSocket("0.0.0.0", port)
        self.client_sock = None
        self.sink = None
        self.query_amount = 4

    def run(self):
        sink = Middleware(ProducerConsumer(Queues.RESULTS))
        print("READY", flush=True)
        with self.socket.accept() as client_sock:
            print("server | connected", flush=True)
            self.client_sock = client_sock
            self.recv_airports(client_sock)
            self.recv_itineraries(client_sock)
            self.send_results(client_sock, sink)
        self.socket.close()
        print("server | disconnected", flush=True)

    def _recv_file(
        self,
        file: str,
        sock: Socket,
        downstream: Middleware,
    ):
        print(f"server | receiving | {file}", flush=True)
        received = 0
        while True:
            batch = Protocol.receive_batch(sock)
            if batch is None:
                print(f"server | EOF | {file}", flush=True)
                break
            received += len(batch)
            self.process_batch(downstream, file, batch)
        downstream.send_message(Protocol.serialize_msg("EOF", [[0]]))
        print(f"server | received | {file} | {received}", flush=True)

    def process_batch(
        self,
        downstream: Middleware,
        file: str,
        batch: list[str],
    ):
        data = list(
            map(
                lambda row: row.split(";" if file == "airports" else ","), batch
            )
        )
        downstream.send_message(Protocol.serialize_msg(file, data))

    def recv_airports(
        self,
        sock: Socket,
    ):
        airports = Middleware(Publisher(Subs.AIRPORTS))
        self._recv_file("airports", sock, airports)
        airports.close_connection()

    def recv_itineraries(
        self,
        sock: Socket,
    ):
        raw_flights = Middleware(ProducerConsumer(Queues.RAW_FLIGHTS))
        self._recv_file("itineraries", sock, raw_flights)
        raw_flights.close_connection()

    def send_results(
        self,
        sock: Socket,
        sink: Middleware,
    ):
        print("server | results", flush=True)

        queries = ["query1", "query2", "query3", "query4"]
        finished = {query: False for query in queries}

        stats = {"query1": 0, "query2": 0, "query3": 0, "query4": 0}

        def handle_message(message: bytes, delivery_tag: int):
            if message is None:
                sink.send_nack(delivery_tag)
                return

            sink.send_ack(delivery_tag)
            header, results = Protocol.deserialize_msg(message)
            if header == "EOF":
                self.query_amount -= 1
                # EOF | [["queryX"]]
                query = results[0][0]
                finished[query] = True
                if self.query_amount != 0 and query == stats.keys():
                    print(
                        f"server | EOF | {query} | {finished} | {stats[query]}",
                        flush=True,
                    )
                if all(finished.values()):
                    sock.send(Protocol.EOF_MESSAGE)
                    sink.close_connection()
                return

            stats[header] += len(results)
            final = [";".join([header, *result]) for result in results]
            sock.send(Protocol.serialize_batch(final))

        sink.get_message(handle_message)

        for query, count in stats.items():
            print(f"server | {query} | {count}", flush=True)
