from middleware_type import MiddlewareType


class PublisherConsumer(MiddlewareType):
    def send_message(self, message):
        return f"sending {message}..."
