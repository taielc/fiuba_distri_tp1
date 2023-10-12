"""Config."""
from os import getenv


DATASET_SIZE = 100000

SERVER_HOST = getenv("SERVER_HOST", "server")
SERVER_PORT = int(getenv("SERVER_PORT", "9000"))
BATCH_SIZE = 5

DEFAULT_INT_SIZE = 4
DEFAULT_ENCODING = "utf-8"

MIN_STOPS_COUNT = 3
DISTANCE_MULTIPLIER = 4

class Queues:
    RESULTS = "results"
    RAW_FLIGHTS = "raw-flights"

    FILTER_BY_STOPS = "filter-by-stops"
    DIST_CALCULATION = "distance-calculation"

    GENERAL_AVG_PRICE = "general-avg-price"
    PARTIAL_ROUTE_AGG = "partial-route-agg"
    FILTER_BY_PRICE = "filter-by-price"

    EXCLUSIVE = ""


class Subs:
    AIRPORTS = "airports"
    FLIGHTS = "flights"
<<<<<<< HEAD
=======
    AVG_PRICE = "avg-price"
>>>>>>> 709b70c15c8c8e98153cb26c4865df4a072060a3
