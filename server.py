import socket
import select
import json
import math

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clients = []


def start():
    global server_socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 5555))
    server_socket.listen(16)


def close():
    server_socket.close()


def accept_clients():
    global server_socket
    if select.select([server_socket], [], [], 0)[0]:
        new_client, addr = server_socket.accept()
        clients.append(new_client)


def broadcast_data(data):
    global clients
    for client in clients:
        try:
            client.send(data)
        except OSError as e:
            print(e)
            clients.remove(client)


def send_json(data):
    data = json.dumps(data).encode("utf-8")+b"\n"
    broadcast_data(data)


def send_labels(state):
    # Easy-to-parse format for microcontrollers
    # Returns results for labels 0, 1, 2, and 3
    bytearr = bytearray()
    for i in range(4):
        labelbytes = bytearray(4)
        if str(i) in state["labels"]:
            label = state["labels"][str(i)]

            labelbytes[0] = label["center"][0]  # Byte 0: X position
            labelbytes[1] = label["center"][1]  # Byte 1: Y position

            headingint = int(label["heading"] / (2*math.pi) * (256**2))
            labelbytes[2] = headingint // 256  # Byte 2: MSByte of heading
            labelbytes[3] = headingint % 256   # Byte 3: LSByte of heading
        bytearr += labelbytes
    broadcast_data(bytes(bytearr))
