"""Config."""
from enum import Enum
from os import getenv


DATASET_SIZE = 100_000

SERVER_HOST = getenv("SERVER_HOST", "server")
SERVER_PORT = int(getenv("SERVER_PORT", "9000"))

DEFAULT_INT_SIZE = 4
DEFAULT_ENCODING = "utf-8"


class Queues:
    RESULTS = "results"
    FLIGHTS_RAW = "flights-raw"
    FILTER_BY_STOPS = "filter-by-stops"



class Subs:
    AIRPORTS = "airports"
    FLIGHTS = "flights"

