"""Csv Reader."""
from typing import TextIO


class Reader:
    def __init__(self, file: TextIO, batch_size=1):
        self.file = file
        self.batch_size = batch_size

    def __iter__(self):
        def _iter():
            line_count = 0
            buffer = []
            for line in self.file:
                line_count += 1
                if line_count == 1:
                    continue
                buffer.append(line.strip())
                if len(buffer) == self.batch_size:
                    yield buffer
                    buffer = []
            if buffer:
                yield buffer

        return _iter()
