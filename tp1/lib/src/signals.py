import signal
import logging


class TerminationSignal(Exception):
    pass


def set_signal_handler(sign: signal.SIGINT | signal.SIGTERM):
    def signal_handler(_signum, _frame):
        logging.info(f"{sign} received")
        raise TerminationSignal(f"{sign} received")

    signal.signal(sign, signal_handler)


def set_termination_signals():
    set_signal_handler(signal.SIGINT)
    set_signal_handler(signal.SIGTERM)


def with_termination_signals(func):
    def wrapper(*args, **kwargs):
        set_termination_signals()
        return func(*args, **kwargs)

    return wrapper
