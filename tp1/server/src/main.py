"""Server main."""

from signals import with_termination_signals
from server import Server


@with_termination_signals
def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
