
from logs import getLogger

import socket
from os import getenv
from multiprocessing import Process

from config import AED_HOST, AED_PORT, node_names, NODE_AMOUNT, TIMEOUT
from heartbeat_listener import HearbeatListener

HOST = AED_HOST
PORT_BASE = AED_PORT

log = getLogger(__name__)


class AED:
    def __init__(self, is_leader) -> None:
        self.is_leader = getenv("LEADER")
        self.processes = []

    def run_healthcheck(self):
        if self.is_leader:
            log.info(f"AED node {HOST} is LEADER")
        
        
        for node_id in range(NODE_AMOUNT):
            listener = HearbeatListener(HOST, PORT_BASE + node_id, TIMEOUT, node_id, self.is_leader)
            log.info(f"Healthcheck for node {node_names[node_id]} listening in host {HOST} and port {PORT_BASE + node_id}")

            p = Process(target=listener.run).start()
            self.processes.append(p)

    def check_group(self):


aed = AED()
Process(target=aed.run_healthcheck).start()
Process(target=aed.check_group).start()

