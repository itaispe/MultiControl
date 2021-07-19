import socket
from tcp_by_size import recv_by_size,send_by_size
from os import system
from subprocess import Popen
IP = "192.168.99.112"
PORT = 12345


def main():
    sock = socket.socket()
    sock.connect((IP,PORT))
    send_by_size(sock,'waiting')
    finished = False
    while not finished:
        data = recv_by_size(sock).decode()
        com = data[:5]
        data = data[5:]
        if com == 'CONNE':
            Popen('python User_client.py '+IP+' True')
            finished = True
        if com == 'STOPP':
            finished = True
    sock.close()

if __name__ == '__main__':
    main()
