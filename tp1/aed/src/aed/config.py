"""Config."""
from os import getenv

AED_HOST = getenv("AED_HOST", "aed")
AED_PORT = getenv("AED_PORT", "aed")

TIMEOUT = 10

NODE_AMOUNT = 5

AED_AMOUNT = 4

node_names = []

aed_data = {1:(HOST1, PORT1), 2:(HOST2, PORT2), 3:(HOST3, PORT3), 4:(HOST4, PORT4), 5:(HOST5, PORT5)}