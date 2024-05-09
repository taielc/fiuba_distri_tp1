"""Config."""
from os import getenv

AED_HOST = getenv("AED_HOST", "aed")
AED_PORT = getenv("AED_PORT", "aed")

TIMEOUT = 10

NODE_AMOUNT = 5

AED_AMOUNT = 4

node_names = []

aed_data = {0:(HOST0, 7000), 1:(HOST1, 7002), 2:(HOST3, 7003), 3:(HOST4, 7004), 4:(HOST5, 7005)}