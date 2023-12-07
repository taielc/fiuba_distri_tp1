from logs import getLogger

import socket
import time

from config import aed_data, AED_AMOUNT


log = getLogger(__name__)

class LeaderElection:
    def __init__(self, host, port, timeout, is_leader, leader_id, aed_id) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(AED_AMOUNT)
        self.socket.settimeout(timeout)     # Cada AED tiene un timeout distinto
        self.is_leader = is_leader
        self.leader_id = leader_id
        self.aed_id = aed_id
        self.other_aed_ids = [x for x in aed_data.keys() if x != aed_id]
        self.election_in_progress = False

    def run(self):
        while True:
            try:
                if self.is_leader:  # Si es lider manda su id a las replicas como PING
                    self.send_leader_data()
                else:   # Si no es lider recibe el id del lider
                    msg = self.receive_msg()
                    msg_data = msg.split(":")
                    flag = msg_data[0]
                    if flag == "LEADER":
                        if msg_data[1] != self.leader_id:
                            self.leader_id = msg_data[1]    # Si el lider cambio, actualizo los datos
                    elif flag == "START_ELECTION":  # No recibe ping del lider => comienza eleccion
                        self.start_election()
                    elif flag == "ELECTION":
                        self.handle_election_message(msg_data[1])
            except Exception as e:
                log.error(f"Error in AED {self.aed_id} | {e}")

    def send_leader_data(self):
        for other_aed_id in self.other_aed_ids:
            data = f"LEADER:{self.aed_id}".encode("utf-8")
            self.send_msg(aed_data[other_aed_id][0], aed_data[other_aed_id][1], data)

    def start_election(self):
        try:
            log.info(f"LEADER IS DOWN. Node {self.aed_id} starts election.")

            aed_data.pop(self.leader_id)    # Elimina de la lista de AEDs el nodo que se cayo

            # Enviar mensajes de eleccion a nodos con identificadores mayores
            higher_nodes = [node for node in aed_data.keys() if node > self.aed_id]
            for higher_node in higher_nodes:
                data = f"ELECTION:{self.aed_id}".encode("utf-8")
                self.send_msg(aed_data[higher_node][0], aed_data[higher_node][1], data)
            
            # Espera respuesta de los nodos con identificadores mayores
            msg = self.receive_msg()
            if msg[0] == "ALIVE":
                return      # No hace nada porque hay un nodo con identificador mayor que esta vivo
        except TimeoutError:    # Ningun otro nodo respondio => este nodo se convierte en lider
            self.is_leader = True
            self.leader_id = self.aed_id 
            log.info(f"Node {self.aed_id} becomes LEADER.")
            self.send_leader_data()     # Envia a todos los nodos los datos del nuevo lider
        
    def handle_election_message(self, lower_node_id):
        print(f"Node {self.aed_id} received election message. Answering ALIVE...")
        # Responde al nodo que inicio la eleccion
        data = f"ALIVE:{self.aed_id}".encode("utf-8")
        self.send_msg(aed_data[lower_node_id][0], aed_data[lower_node_id][0], data)
        self.start_election()       # Comienza la eleccion de nuevo con los nodos mayores a mi

    def receive_msg(self):
        while True:
            try:
                data = self.recv(1024)
                if not data:
                    break
            except TimeoutError:   # No responde el lider
                return "START_ELECTION"
        return data.decode("utf-8")

    def recv(self, size: int):
        parts: list[bytes] = []
        while size:
            part = self.socket.recv(size)
            if not part:
                raise SystemError("Connection closed")
            parts.append(part)
            size -= len(part)
        return b"".join(parts)

    def send_msg(self, other_aed_host, other_aed_port, data):
        self.socket.connect(other_aed_host, other_aed_port)
        while True:
            self.socket.sendall(data)   # El lider envia su id
            time.sleep(5)  # Intervalo entre envios de "ping"
