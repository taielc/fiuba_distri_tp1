from os import getenv


REPLICAS = int(getenv("REPLICAS", 1))
WORKER_NAME = getenv("WORKER_NAME", "worker")
