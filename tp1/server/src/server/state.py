from enum import Enum


class State(Enum):
    INIT = 0
    RECVING_AIRPORTS = 1
    RECVING_ITINERARIES = 2
    SENDING_RESULTS = 3
    DONE = 4

    def is_done(self):
        return self == State.DONE

    def get_next(self):
        return State(self.value + 1)
