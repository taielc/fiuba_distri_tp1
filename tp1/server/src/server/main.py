"""Server main."""

from middleware import Middleware
from tcp import ServerSocket


def main():
    socket = ServerSocket("0.0.0.0", 9000)
    with socket.accept() as peer:
        msg = peer.recv(12)
        print("server received:", msg)
        peer.send(msg)
    socket.close()

if __name__ == "__main__":
    main()
