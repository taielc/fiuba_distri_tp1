"""Config."""
from os import getenv


DATASET_SIZE = 100_000

SERVER_HOST = getenv("SERVER_HOST", "server")
SERVER_PORT = int(getenv("SERVER_PORT", "9000"))

DEFAULT_INT_SIZE = 4
DEFAULT_ENCODING = "utf-8"
