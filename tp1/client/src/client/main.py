"""Client main."""

from tcp import Socket


def main():
    with Socket("server", 9000) as socket:
        socket.send(b"Hello world!")
        print(socket.recv(12))


if __name__ == "__main__":
    main()
