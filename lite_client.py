import socket
import math
import binascii
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

MY_NUM = 0
TARGET_NUM = 1


def connect(host=sys.argv[1], port=5556):
    global sock
    sock.connect((host, port))


def get_state():
    global sock
    data = sock.recv(16)
    return bytearray(data)


def close():
    global sock
    sock.close()


def get_label(num):
    my_bytes = state[num*4: num*4 + 4]
    x, y = (my_bytes[0] - 128)/4, (my_bytes[1] - 128)/4
    heading = (my_bytes[2]*256 + my_bytes[3]) / (256 ** 2) * math.pi * 2
    return x, y, heading


if __name__ == "__main__":
    connect()

    try:
        while True:
            state = get_state()
            print(binascii.hexlify(state, " ").decode("utf-8"))

            myx, myy, myh = get_label(MY_NUM)
            tax, tay, tah = get_label(TARGET_NUM)
            glob_h = math.atan2(tay-myy, tax-myx)

            print(f"Me: ({myx}, {myy}, {myh} rad)."
                  f"Target: ({tax}, {tay}, {tah} rad).")

    finally:
        close()
