"""Client socket implementation."""
from socket import socket
from typing import Callable
import re

from .factory import create_socket
from .errors import SocketError


def _assert_connected(method):
    # add "PRE: is connected" to method docstring, before first doctest

    def wrapper(self: "Socket", *args, **kwargs):
        if not self._connected:  # pylint: disable=protected-access
            raise SocketError("Not connected")
        return method(self, *args, **kwargs)

    cond = "**PRE:** is connected"
    wrapper.__doc__ = (
        cond
        if method.__doc__ is None
        else re.sub(
            r"(?P<indent>\s*)(\>\>\>)",
            rf"\1\n{cond}\n\n\1\2",
            method.__doc__,
            count=1,
        )
    )
    return wrapper


class Socket:
    def __init__(
        self,
        host: str,
        port: int,
        factory: Callable[[], socket] = create_socket,
    ):
        self.sock = factory()
        self.host = host
        self.port = port
        self._connected = False

    def connect(self):
        if self._connected:
            raise SocketError("Already connected")
        self.sock.connect((self.host, self.port))
        self._connected = True
        return self

    def __enter__(self) -> "Socket":
        return self.connect()

    def __exit__(self, *args):
        self.close()

    @_assert_connected
    def send(self, data: bytes):
        """Send data, avoiding short writes

        >>> sock.send(b"hello")
        >>> sock.send(b"world")
        """
        self.sock.sendall(data)

    @_assert_connected
    def recv(self, size: int):
        """Receive data, avoiding short reads

        >>> sock.recv(5)
        b'hello'
        >>> sock.recv(5)
        b'world'
        """
        parts: list[bytes] = []
        while size:
            part = self.sock.recv(size)
            if not part:
                raise SocketError("Connection closed")
            parts.append(part)
            size -= len(part)
        return b"".join(parts)

    def close(self):
        if not self._connected:
            return
        self.sock.close()
        self._connected = False

    def __del__(self):
        self.close()


if __debug__:
    from unittest.mock import Mock
    from pytest import fixture

    create_mock = Mock()
    mock_sock = Mock()
    mock_sock.connect.return_value = None
    mock_sock.recv.side_effect = [b"hello", b"world"]
    create_mock.return_value = mock_sock
    sock = Socket(
        "localhost",
        8080,
        factory=create_mock,
    )
    sock.connect()

    @fixture(autouse=True)
    def doctest_extraglobs(doctest_namespace):
        doctest_namespace["sock"] = sock

    # mock_sock.sendall.assert_has_calls([call(b"hello"), call(b"world")])
