import socket
import json
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

MY_NUM = 0


def connect(host=sys.argv[1], port=5555):
    global sock
    sock.connect((host, port))


def get_state():
    global sock
    return json.loads(sock.recv(1024).decode("utf-8").split("\n")[-2])


def close():
    global sock
    sock.close()


if __name__ == "__main__":
    connect()

    try:
        while True:
            state = get_state()

            if str(MY_NUM) not in state["labels"]:
                continue

            pos = state["labels"][str(MY_NUM)]["center"]
            heading = state["labels"][str(MY_NUM)]["heading"]
            print(pos, heading)
    finally:
        close()
