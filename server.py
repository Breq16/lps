import socket
import select
import json
import math

import numpy as np


class LPSServer:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.clients = []

    def start(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("0.0.0.0", self.port))
        self.socket.listen(16)

    def close(self):
        self.socket.close()

    def accept(self):
        if select.select([self.socket], [], [], 0)[0]:
            new_client, addr = self.socket.accept()
            self.clients.append(new_client)

    def broadcast(self, data):
        for client in self.clients:
            try:
                client.send(data)
            except OSError as e:
                print(e)
                self.clients.remove(client)

    def update(self, state):
        pass


class JSONServer(LPSServer):
    def __init__(self):
        super().__init__(5555)

    def update(self, state):
        data = json.dumps(state).encode("utf-8")+b"\n"
        self.broadcast(data)


class LiteServer(LPSServer):
    def __init__(self):
        super().__init__(5556)

    def update(self, state):
        # Easy-to-parse format for microcontrollers
        # Returns results for labels 0, 1, 2, and 3
        bytearr = bytearray()
        for i in range(4):
            labelbytes = bytearray(4)
            if str(i) in state["labels"]:
                label = state["labels"][str(i)]

                # Byte 0: Xpos (1/4 unit)
                labelbytes[0] = np.clip(int(label["center"][0]*4 + 128),
                                        0, 255)
                # Byte 1: Ypos (1/4 unit)
                labelbytes[1] = np.clip(int(label["center"][1]*4 + 128),
                                        0, 255)

                heading = label["heading"]
                if heading < 0:
                    heading += 2 * math.pi
                headingint = int(heading / (2*math.pi) * (256**2))
                # Byte 2: MSByte of heading
                labelbytes[2] = min(headingint // 256, 255)
                labelbytes[3] = headingint % 256   # Byte 3: LSByte of heading
            bytearr += labelbytes
        self.broadcast(bytes(bytearr))


servers = [JSONServer(), LiteServer()]


def start():
    for server in servers:
        server.start()


def close():
    for server in servers:
        server.close()


def accept():
    for server in servers:
        server.accept()


def update(state):
    for server in servers:
        server.update(state)
