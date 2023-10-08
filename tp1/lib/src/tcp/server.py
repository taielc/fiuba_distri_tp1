"""Server socket"""
from socket import socket

from .factory import create_socket
from .socket import Socket


class PeerSocket(Socket):
    def __init__(self, sock: socket, addr: tuple[str, int]):
        super().__init__(addr[0], addr[1], factory=lambda: sock)
        self._connected = True

    def __enter__(self) -> "PeerSocket":
        return self


class ServerSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = create_socket()
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

    def accept(self) -> Socket:
        return PeerSocket(*self.sock.accept())

    def close(self):
        self.sock.close()
