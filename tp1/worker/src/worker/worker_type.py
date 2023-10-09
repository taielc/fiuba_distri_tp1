from enum import Enum


class WorkerType(str, Enum):
    FILTER = "FILTER"


class WorkerBase:
    def run(self):
        raise NotImplementedError()
