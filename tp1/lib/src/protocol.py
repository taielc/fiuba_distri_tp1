from typing import Any

from serde import ser_str, de_str, ser_int, de_int, DEFAULT_INT_SIZE
from tcp.socket import Socket


_ROW_SEP = "\n"
_VALUE_SEP = ";"


class Protocol:
    EOF_MESSAGE = ser_int(0)
    ACK_MESSAGE = ser_int(0)

    @staticmethod
    def serialize_batch(batch: list[str]) -> bytes:
        ser_batch = ser_str(_ROW_SEP.join(map(str, batch)))
        return ser_int(len(ser_batch)) + ser_batch

    @staticmethod
    def receive_batch(sock: Socket) -> list[str]:
        size = de_int(sock.recv(DEFAULT_INT_SIZE))
        if size == 0:
            return None
        batch = de_str(sock.recv(size))
        return batch.split(_ROW_SEP)

    @staticmethod
    def serialize_msg(header: str, data: list[list[Any]]) -> bytes:
        def ser_row(row: list[Any]) -> bytes:
            return _VALUE_SEP.join(map(str, row))

        return ser_str(header + _ROW_SEP) + ser_str(
            _ROW_SEP.join(map(ser_row, data))
        )

    @staticmethod
    def deserialize_msg(data: bytes) -> [str, list[list[Any]]]:
        str_data = de_str(data)
        header, str_rows = str_data.split(_ROW_SEP, 1)
        return header, [
            row.split(_VALUE_SEP) for row in str_rows.split(_ROW_SEP)
        ]
