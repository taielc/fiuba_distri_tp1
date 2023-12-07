from logs import getLogger

import socket
import subprocess
from config import node_names


log = getLogger(__name__)

class HearbeatListener:
    def __init__(self, host, port, timeout, node_id, is_leader) -> None:
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind((host, port))
        self.listener_socket.listen(1)
        self.listener_socket.settimeout(timeout)
        self.node_id = node_id
        self.is_leader = is_leader

    def accept_connections(self):
        try:
            conn, addr = self.listener_socket.accept()
            log.info(
                f'accept connection for node_id: {self.node_id} | IP: {addr[0]}')
            return conn
        except socket.timeout:
            return None
    
    def run(self):
        sock = self.accept_connections()
        while True:
            try:
                self.recv(sock, 1)
            except TimeoutError:
                if self.is_leader:  # solo reinicia si es lider, sino ignora
                    self.restart_node(self.node_id)
                    sock = self.accept_connections()
                    while not sock:
                        self.restart_node(self.node_id)
                        sock = self.accept_connections()

    def recv(self, sock, size: int):
        parts: list[bytes] = []
        while size:
            part = sock.recv(size)
            if not part:
                raise SystemError("Connection closed")
            parts.append(part)
            size -= len(part)
        return b"".join(parts)

    def restart_node(self):
        node_name = node_names[self.node_id]
        log.info(f"The node {node_name} will be restarted")
        r = subprocess.run(['docker', 'start', node_name], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.info(f"The node {node_name} was restarted | {r.returncode} | {r.stdout} | {r.stderr}")
