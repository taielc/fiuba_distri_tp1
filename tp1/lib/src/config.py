"""Config."""
from enum import Enum
from os import getenv


DATASET_SIZE = 100_000

SERVER_HOST = getenv("SERVER_HOST", "server")
SERVER_PORT = int(getenv("SERVER_PORT", "9000"))

DEFAULT_INT_SIZE = 4
DEFAULT_ENCODING = "utf-8"


class Queues(str, Enum):
    """Common queues names.

    Use as `str(Queues.NAME)`
    """

    RESULTS = "results"
    FLIGHTS_RAW = "flights-raw"
    FILTER_BY_STOPS = "filter-by-stops"

    def __str__(self):
        return self.value


class Subs(str, Enum):
    """Common subscription names.

    Use as `str(Subs.NAME)`
    """

    AIRPORTS = "airports"
    FLIGHTS = "flights"

    def __str__(self):
        return self.value
