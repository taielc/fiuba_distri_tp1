from pathlib import Path

from tcp import Socket
from protocol import Protocol
from config import SERVER_HOST, SERVER_PORT

from .config import AIRPORTS_FILE, ITINERARIES_FILE
from .state import State
from .reader import Reader


class Client:
    def __init__(
        self,
        host: str = SERVER_HOST,
        port: int = SERVER_PORT,
        airports: Path = AIRPORTS_FILE,
        itineraries: Path = ITINERARIES_FILE,
    ):
        self.state = State.INIT
        self.host = host
        self.port = port
        self.airports = airports
        self.itineraries = itineraries
        self._handlers = {
            State.SENDING_AIRPORTS: self.send_airports,
            State.SENDING_ITINERARIES: self.send_itineraries,
            State.RECVING_RESULTS: self.recv_results,
        }

    def run(self):
        print("client | state | INIT")
        with Socket(self.host, self.port) as sock:
            self.state = State.SENDING_AIRPORTS
            print("client | state | SENDING_AIRPORTS")
            self.run_state_machine(sock)

    def run_state_machine(self, sock: Socket):
        while not self.state.is_done():
            handler = self._handlers[self.state]
            handler(sock)
            self.state = self.state.get_next()

    def _send_file(self, sock: Socket, file: Path):
        print(f"client | sending file | {file}")
        count = 0
        with file.open("rt") as f:
            for batch in Reader(f):
                count += len(batch)
                print("client | batch |", batch)
                sock.send(Protocol.serialize_batch(batch))
                if count % 10000 == 0:
                    print(f"client | sent | {count}")
                if count >= 10:
                    break
            sock.send(Protocol.EOF_MESSAGE)

    def send_airports(self, sock: Socket):
        self._send_file(sock, self.airports)

    def send_itineraries(self, sock: Socket):
        self._send_file(sock, self.itineraries)

    def recv_results(self, sock: Socket):
        while True:
            data = Protocol.receive_batch(sock)
            if data is None:
                break
            for result in data:
                print(result)
