"""Worker main."""
from importlib import import_module
from sys import argv

from signals import with_termination_signals
from logs import getLogger

log = getLogger(__name__)


@with_termination_signals
def main():
    worker_name = argv[1]
    log.hinfo("starting")
    worker_module = import_module(f"worker.{worker_name}")
    worker_module.main()
    log.hinfo("done")


if __name__ == "__main__":
    main()
