from os import getenv

from .worker_type import WorkerType


WORKER_NAME = getenv("WORKER_NAME")
WORKER_TYPE = WorkerType[getenv("WORKER_TYPE")]

UPSTREAM_QUEUE = getenv("UPSTREAM_QUEUE")
DOWNSTREAM_QUEUE = getenv("DOWNSTREAM_QUEUE")
