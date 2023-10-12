from logging import getLogger

from config import SERVER_PORT, Queues, Subs
from middleware import Middleware, PublisherConsumer, PublisherSuscriber
from protocol import Protocol
from tcp import ServerSocket, Socket

log = getLogger(__name__)


class Server:
    def __init__(self, port: int = SERVER_PORT):
        self.port = port
        self.socket = ServerSocket("0.0.0.0", port)
        self.client_sock = None
        self.sink = None

    def run(self):
        sink = Middleware(PublisherConsumer(Queues.RESULTS))
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
        airports = Middleware(PublisherSuscriber("", Subs.AIRPORTS))
        self._recv_file("airports", sock, airports)
        airports.close_connection()

    def recv_itineraries(
        self,
        sock: Socket,
    ):
        raw_flights = Middleware(PublisherConsumer(Queues.RAW_FLIGHTS))
        self._recv_file("itineraries", sock, raw_flights)
        raw_flights.close_connection()

    def send_results(
        self,
        sock: Socket,
        sink: Middleware,
    ):
        print("server | results", flush=True)
        sock.send(
            Protocol.serialize_batch(
                [["example", "result1"], ["example", "result2"]]
            )
        )

        queries_results = [False, False]

        def handle_message(message: bytes, delivery_tag: int):
            if message is None:
                sink.send_nack(delivery_tag)
                return

            sink.send_ack(delivery_tag)
            header, results = Protocol.deserialize_msg(message)
            print(f"server | msg | {header} | {len(results)}", flush=True)
            if header == "EOF":
                query = results[0][0]
                queries_results[int(query.lstrip("query")) - 1] = True
                print(f"server | EOF | {query} | {queries_results}", flush=True)
                if all(queries_results):
                    sock.send(Protocol.EOF_MESSAGE)
                    sink.close_connection()
                return
            sock.send(Protocol.serialize_batch(results))

        sink.get_message(handle_message)
