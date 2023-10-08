"""Csv Reader."""
from typing import TextIO


class Reader:
    def __init__(self, file: TextIO, batch_size=1):
        self.file = file
        self.batch_size = batch_size
        self.buffer = []
        

    def __iter__(self):
        def _iter():
            line_count = 0
            for line in self.file:
                line_count += 1
                if line_count == 1:
                    continue
                self.buffer.append(line)
                if len(self.buffer) == self.batch_size:
                    yield self.buffer
                    self.buffer = []
            
        return _iter()
