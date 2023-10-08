from tcp import ServerSocket, Socket
from protocol import Protocol
from logging import getLogger

from config import SERVER_PORT

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
        with self.socket.accept() as client_sock:
            self.state = State.RECVING_AIRPORTS
            self.run_state_machine(client_sock)

    def run_state_machine(self, sock: Socket):
        while not self.state.is_done():
            handler = self._handlers[self.state]
            handler(sock)
            self.state = self.state.get_next()

    def _recv_file(self, sock: Socket, file: str):
        print(f"server | receiving | {file}")
        received = 0
        while True:
            batch = Protocol.receive_batch(sock)
            if batch is None:
                print(f"server | EOF | {file}")
                break
            received += len(batch)
            # self.middleware.process_batch(file, batch)
        print(f"server | received | {file} | {received}")

    def recv_airports(self, sock: Socket):
        self._recv_file(sock, "airports")

    def recv_itineraries(self, sock: Socket):
        self._recv_file(sock, "itineraries")

    def send_results(self, sock: Socket):
        # results = self.middleware.get_results()
        # sock.send(Protocol.serialize_batch(results))
        sock.send(
            Protocol.serialize_batch(["query1,result1", "query2,result1"])
        )
        sock.send(Protocol.EOF_MESSAGE)
