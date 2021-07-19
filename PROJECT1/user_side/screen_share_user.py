import socket
from tcp_by_size import send_by_size, recv_by_size
from zlib import compress
import pyautogui
from mss import mss

WIDTH, HEIGHT = pyautogui.size()
PORT = 1234


def share_screen(ip):
    """connecting to admin and sending screen photos"""
    sock = socket.socket()
    sock.connect((ip, PORT))
    send_by_size(sock, 'SSIZE' + str(WIDTH) + '#' + str(HEIGHT))
    with mss() as sct:
        finish = False
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}
        while not finish:
            sock.settimeout(0.1)
            try:
                try:
                    data = recv_by_size(sock)
                    if data.decode() == 'ENDST':
                        finish = True
                except socket.timeout:
                    sock.settimeout(None)
                    img = sct.grab(rect)
                    pixels = compress(img.rgb, 1)
                    send_by_size(sock, 'PIXEL'.encode() + pixels, True)
            except ConnectionResetError:
                break


if __name__ == '__main__':
    share_screen('192.168.68.110')
