"""Config."""
from os import getenv


DATASET_SIZE = 100000

SERVER_HOST = getenv("SERVER_HOST", "server")
SERVER_PORT = int(getenv("SERVER_PORT", "9000"))
BATCH_SIZE = 5

DEFAULT_INT_SIZE = 4
DEFAULT_ENCODING = "utf-8"

MIN_STOPS_COUNT = 3

class Queues:
    RESULTS = "results"
    RAW_FLIGHTS = "raw-flights"
    FILTER_BY_STOPS = "filter-by-stops"
    DIST_CALCULATION = "distance-calculation"

    EXCLUSIVE = ""



class Subs:
    AIRPORTS = "airports"
    FLIGHTS = "flights"

