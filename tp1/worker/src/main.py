"""Worker main."""
from importlib import import_module
from sys import argv

from signals import with_termination_signals


@with_termination_signals
def main():
    worker_name = argv[1]
    print("starting")
    worker_module = import_module(f"worker.{worker_name}")
    worker_module.main()
    print("done", flush=True)


if __name__ == "__main__":
    main()
