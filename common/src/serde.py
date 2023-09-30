"""Basic serialization and deserialization functions."""

from config import DEFAULT_INT_SIZE, DEFAULT_ENCODING

def ser_int(value: int, size: int = DEFAULT_INT_SIZE) -> bytes:
    """Serialize int.
    
    >>> ser_int(42)
    b'\\x00\\x00\\x00*'
    >>> ser_int(42, size=2)
    b'\\x00*'
    >>> ser_int(150)
    b'\\x00\\x00\\x00\\x96'
    >>> ser_int(0, size=2)
    b'\\x00\\x00'
    """
    return value.to_bytes(size, "big")

def de_int(data: bytes, size: int = DEFAULT_INT_SIZE) -> int:
    """Deserialize first `size` bytes into an integer.
    
    >>> de_int(b'\\x00\\x00\\x00*')
    42
    >>> de_int(b'\\x00*')
    42
    >>> de_int(b'\\x00\\x00\\x00\\x96')
    150
    >>> de_int(b'\\x00\\x00', size=2)
    0
    """
    return int.from_bytes(data[:size], "big")


def ser_str(value: str, encoding: str = DEFAULT_ENCODING) -> bytes:
    """Serialize string.
    
    >>> ser_str("hello")
    b'hello'
    >>> ser_str("hello", encoding="utf-16")
    b'\\xff\\xfeh\\x00e\\x00l\\x00l\\x00o\\x00'
    """
    return value.encode(encoding)


def de_str(data: bytes, encoding: str = DEFAULT_ENCODING) -> str:
    """Deserialize a string 
    
    >>> de_str(b'hello')
    'hello'
    >>> de_str(b'\\xff\\xfeh\\x00e\\x00l\\x00l\\x00o\\x00', encoding="utf-16")
    'hello'
    """
    return data.decode(encoding)

if __debug__:
    from utils import run_doctest
    run_doctest(__name__)
