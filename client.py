import socket
import json
import turtle

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

MY_NUM = 2


def connect(host="localhost", port=5555):
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
            turtle._Screen._root.update()
            state = get_state()
            my_marker = None
            for marker in state:
                if marker["num"] == MY_NUM:
                    my_marker = marker

            if my_marker is None:
                continue

            if my_marker["pos"] is None:
                continue

            pos = tuple(int(coord*10) for coord in my_marker["pos"])
            front = tuple(int(coord*10) for coord in my_marker["front"])
            print(pos, front)
            turtle.goto(pos)
            heading = turtle.towards(front)
            turtle.setheading(heading)
    finally:
        close()
