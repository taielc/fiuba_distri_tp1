from .middleware import Middleware
from .publisher_consumer import PublisherConsumer
from .publisher_suscriber import PublisherSuscriber

# middleware1 = Middleware(PublisherSuscriber())
# middleware1.send_message("ffdsfds")

middleware2 = Middleware(PublisherConsumer("helloq"))
middleware2.send_message("Hello World!")

middleware2.close_connection()
