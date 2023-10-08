"""Client states."""
from enum import Enum


class State(Enum):
    INIT = 0
    SENDING_AIRPORTS = 1
    SENDING_ITINERARIES = 2
    RECVING_RESULTS = 3
    DONE = 4

    def is_done(self):
        return self == State.DONE

    def get_next(self):
        return State(self.value + 1)
