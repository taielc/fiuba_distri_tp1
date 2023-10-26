from typing import Any
from serde import ser_str, de_str

_ROW_SEP = "\n"
_VALUE_SEP = ";"


class Message:
    @classmethod
    def EOF(cls) -> bytes:
        return cls.serialize_msg("EOF", [[0]])

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
