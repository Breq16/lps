import socket
import select
import json

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
