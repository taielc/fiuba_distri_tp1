"""Client main."""

from signals import with_termination_signals
from client import Client


@with_termination_signals
def main():
    client = Client()
    client.run()


if __name__ == "__main__":
    main()
