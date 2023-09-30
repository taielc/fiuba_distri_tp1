from middleware import Middleware
from publisher_consumer import PublisherConsumer
from publisher_suscriber import PublisherSuscriber


middleware1 = Middleware(PublisherSuscriber())
middleware2 = Middleware(PublisherConsumer())


middleware1.send_message("ffdsfds")
middleware2.send_message("vdsfdfv")
