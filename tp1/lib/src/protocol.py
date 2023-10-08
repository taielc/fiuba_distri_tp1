from serde import ser_str, de_str, ser_int, de_int, DEFAULT_INT_SIZE
from tcp.socket import Socket


_SEP = ";"


class Protocol:
    EOF_MESSAGE = ser_int(0)

    @staticmethod
    def serialize_batch(batch: list[str]) -> bytes:
        ser_batch = ser_str(_SEP.join(map(str, batch)))
        return ser_int(len(ser_batch)) + ser_batch

    @staticmethod
    def receive_batch(sock: Socket) -> list[str]:
        size = de_int(sock.recv(DEFAULT_INT_SIZE))
        if size == 0:
            return None
        batch = de_str(sock.recv(size))
        return batch.split(_SEP)
