"""Config."""
from os import getenv


DATASET_SIZE = 10_000_000
LOGGING_LEVEL = getenv("LOGGING_LEVEL", "HINFO")

SERVER_HOST = getenv("SERVER_HOST", "server")
SERVER_PORT = 9000
MIDDLEWARE_HOST = "middleware"

BATCH_SIZE = 50
DEFAULT_INT_SIZE = 4
DEFAULT_ENCODING = "utf-8"

MIN_STOPS_COUNT = 3
DISTANCE_MULTIPLIER = 4


class Queues:
    RESULTS = "results"
    RAW_FLIGHTS = "raw-flights"

    # 1
    FILTER_BY_STOPS = "filter-by-stops"
    # 2
    DIST_CALCULATION = "distance-calculation"
    # 3
    PARTIAL_ROUTE_AGG = "partial-route-agg"
    TOP_2_FASTESTS_BY_ROUTE = "top-2-fastests-by-route"
    # 4
    GENERAL_AVG_PRICE = "general-avg-price"
    FILTER_BY_PRICE = "filter-by-price"
    PRICE_BY_ROUTE = "price-by-route"


class Subs:
    AIRPORTS = "airports"
    FLIGHTS = "flights"
    AVG_PRICE = "avg-price"
