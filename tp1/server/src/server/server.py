from logging import getLogger

from config import SERVER_PORT, Queues
from middleware_v2 import MiddlewareV2
from protocol import Protocol
from tcp import ServerSocket, Socket

log = getLogger(__name__)


class Server:
    def __init__(self, port: int = SERVER_PORT):
        self.port = port
        self.socket = ServerSocket("0.0.0.0", port)
        self.client_sock = None
        self.sink = None
        self.downstream = Queues.FLIGHTS_RAW
        self.results = Queues.RESULTS

    def run(self):
        middleware = MiddlewareV2()
        middleware.consume(self.results, self._consume_results)
        with self.socket.accept() as client_sock:
            print("server | connected", flush=True)
            self.client_sock = client_sock
            self.recv_airports(client_sock, middleware)
            self.recv_itineraries(client_sock, middleware)
            middleware.push(
                self.downstream, Protocol.serialize_msg("EOF", [[0]])
            )
            self.send_results(client_sock, middleware)
        self.socket.close()
        print("server | disconnected", flush=True)

    def _recv_file(
        self,
        file: str,
        sock: Socket,
        middleware: MiddlewareV2,
    ):
        print(f"server | receiving | {file}", flush=True)
        received = 0
        while True:
            batch = Protocol.receive_batch(sock)
            if batch is None:
                print(f"server | EOF | {file}", flush=True)
                break
            received += len(batch)
            self.process_batch(middleware, file, batch)
        print(f"server | received | {file} | {received}", flush=True)

    def process_batch(
        self,
        middleware: MiddlewareV2,
        file: str,
        batch: list[str],
    ):
        data = list(map(lambda row: row.split(";"), batch))
        middleware.push(self.downstream, Protocol.serialize_msg(file, data))

    def recv_airports(
        self,
        sock: Socket,
        middleware: MiddlewareV2,
    ):
        self._recv_file("airports", sock, middleware)

    def recv_itineraries(
        self,
        sock: Socket,
        middleware: MiddlewareV2,
    ):
        self._recv_file("itineraries", sock, middleware)

    def _consume_results(
        self,
        mid: MiddlewareV2,
        msg: bytes,
    ):
        header, data = Protocol.deserialize_msg(msg)
        print(f"server | msg | {header} | {len(data)}", flush=True)
        if header == "EOF":
            self.client_sock.send(Protocol.EOF_MESSAGE)
            mid.cancel(self.results)
            return

        self.client_sock.send(Protocol.serialize_batch(data))

    def send_results(
        self,
        sock: Socket,
        middleware: MiddlewareV2,
    ):
        print("server | results", flush=True)
        sock.send(
            Protocol.serialize_batch(
                [["example", "result1"], ["example", "result2"]]
            )
        )
        middleware.start()

    def handle_message(self, message, delivery_tag):
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
