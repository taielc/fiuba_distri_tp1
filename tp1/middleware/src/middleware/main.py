<<<<<<< HEAD:middleware/src/main.py
from middleware import Middleware
from publisher_consumer import PublisherConsumer
# from publisher_suscriber import PublisherSuscriber
=======
from .middleware import Middleware
from .publisher_consumer import PublisherConsumer
from .publisher_suscriber import PublisherSuscriber
>>>>>>> f2229d0cba38a77b28697bbb434b8f6824443fa0:tp1/middleware/src/middleware/main.py

# middleware1 = Middleware(PublisherSuscriber())
# middleware1.send_message("ffdsfds")

middleware2 = Middleware(PublisherConsumer("helloq"))
middleware2.send_message("Hello World!")

middleware2.close_connection()
