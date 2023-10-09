from .middleware_type import MiddlewareType


class Middleware:
    def __init__(self, type: MiddlewareType):
        self._type = type

    @property
    def type(self) -> MiddlewareType:
        return self._type

    @type.setter
    def type(self, type: MiddlewareType) -> None:
        self._type = type

    def send_message(self, message):
        self._type.send_message(message)

    def get_message(self):
        return self._type.get_message()

    def close_connection(self):
        self._type.close_connection()
