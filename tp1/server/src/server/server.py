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
        pipeline = Middleware(PublisherConsumer(Queues.FLIGHTS_RAW))
        self.sink = Middleware(PublisherConsumer(Queues.RESULTS))
        with self.socket.accept() as client_sock:
            print("server | connected")
            self.client_sock = client_sock
            self.recv_airports(client_sock, pipeline)
            self.recv_itineraries(client_sock, pipeline)
            self.send_results(client_sock)
        self.socket.close()
        print("server | disconnected")

    def _recv_file(
        self,
        file: str,
        sock: Socket,
        pipeline: Middleware,
    ):
        print(f"server | receiving | {file}")
        received = 0
        while True:
            batch = Protocol.receive_batch(sock)
            if batch is None:
                print(f"server | EOF | {file}")
                break
            received += len(batch)
            self.process_batch(pipeline, file, batch)
        print(f"server | received | {file} | {received}")

    def process_batch(
        self,
        pipeline: Middleware,
        file: str,
        batch: list[str],
    ):
        data = list(map(lambda row: row.split(";"), batch))
        pipeline.send_message(Protocol.serialize_msg(file, data))

    def recv_airports(
        self,
        sock: Socket,
        pipeline: Middleware,
    ):
        self._recv_file("airports", sock, pipeline)

    def recv_itineraries(
        self,
        sock: Socket,
        pipeline: Middleware,
    ):
        self._recv_file("itineraries", sock, pipeline)

    def send_results(
        self,
        sock: Socket,
    ):
        print("server | results")
        sock.send(
            Protocol.serialize_batch(["example;result1", "example;result2"])
        )

        self.sink.get_message(self.handle_message)

        self.sink.close_connection()

    def handle_message(self, message: bytes, delivery_tag: int):
        print("message is: ", message)
        if message is None:
            self.sink.send_nack(delivery_tag)
            return

        self.sink.send_ack(delivery_tag)
        header, results = Protocol.deserialize_msg(message)
        print(f"server | msg | {header} | {len(results)}")
        if header == "EOF":
            self.client_sock.send(Protocol.EOF_MESSAGE)
            self.sink.close_connection()
            return
        self.client_sock.send(Protocol.serialize_batch(results))
