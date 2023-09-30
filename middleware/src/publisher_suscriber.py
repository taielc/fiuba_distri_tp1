from middleware_type import MiddlewareType


class PublisherSuscriber(MiddlewareType):
    def send_message(self, message):
        return f"sending {message}..."
