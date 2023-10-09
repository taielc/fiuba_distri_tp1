from logging import getLogger

from config import SERVER_PORT
from middleware import Middleware, PublisherConsumer
from protocol import Protocol
from tcp import ServerSocket, Socket

from .state import State


log = getLogger(__name__)


class Server:
    def __init__(self, port: int = SERVER_PORT):
        self.port = port
        self.socket = ServerSocket("0.0.0.0", port)
        self.state = State.INIT
        # self.middleware = Middleware()
        self._handlers = {
            State.RECVING_AIRPORTS: self.recv_airports,
            State.RECVING_ITINERARIES: self.recv_itineraries,
            State.SENDING_RESULTS: self.send_results,
        }

    def run(self):
        pipeline = Middleware(PublisherConsumer("source"))
        sink = Middleware(PublisherConsumer("results"))
        with self.socket.accept() as client_sock:
            self.state = State.RECVING_AIRPORTS
            self.run_state_machine(client_sock, pipeline, sink)

    def run_state_machine(
        self,
        sock: Socket,
        pipeline: Middleware,
        sink: Middleware,
    ):
        while not self.state.is_done():
            handler = self._handlers[self.state]
            handler(sock, pipeline, sink)
            self.state = self.state.get_next()

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
        print("server | batch |", batch)
        if file == "itineraries":
            batch = list(map(lambda row: row.replace(",", ";"), batch))
        pipeline.send_message(Protocol.serialize_msg(file, batch))

    def recv_airports(
        self,
        sock: Socket,
        pipeline: Middleware,
        _sink: Middleware,
    ):
        self._recv_file("airports", sock, pipeline)

    def recv_itineraries(
        self,
        sock: Socket,
        pipeline: Middleware,
        _sink: Middleware,
    ):
        self._recv_file("itineraries", sock, pipeline)

    def send_results(
        self,
        sock: Socket,
        _pipeline: Middleware,
        sink: Middleware,
    ):
        print("server | results")
        while True:
            message, post_hook = sink.get_message()
            if message is None:
                continue
            post_hook()

            header, results = Protocol.deserialize_msg(message)
            print(f"server | msg | {header} | {len(results)}")
            if header == "EOF":
                break

            sock.send(Protocol.serialize_batch(results))
        sock.send(Protocol.EOF_MESSAGE)
