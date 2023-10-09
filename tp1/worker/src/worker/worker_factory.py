from middleware import Middleware, PublisherConsumer

from .config import WORKER_NAME, WORKER_TYPE
from .worker_type import WorkerType, WorkerBase


class WorkerFactory:
    @staticmethod
    def create_worker(
        worker_name: str = WORKER_NAME,
        worker_type: WorkerType = WORKER_TYPE,
    ) -> WorkerBase:
        match worker_type:
            case WorkerType.FILTER:
                # pylint: disable=import-outside-toplevel
                from .filter import Filter
                from .config import UPSTREAM_QUEUE, DOWNSTREAM_QUEUE

                upstream = Middleware(PublisherConsumer(UPSTREAM_QUEUE))
                downstream = Middleware(PublisherConsumer(DOWNSTREAM_QUEUE))
                return Filter(
                    worker_name,
                    upstream,
                    downstream,
                )
            case _:
                raise ValueError(f"Invalid worker type: {WORKER_TYPE}")
