import socket
from zlib import decompress
import pygame
from tcp_by_size import recv_by_size,send_by_size
import threading
import pyautogui
IP = '0.0.0.0'
PORT = 1234
WIDTH ,HEIGHT = pyautogui.size()
PIC_X = 1920
PIC_Y = 1080
running_lock = threading.Lock()
num_lock = threading.Lock()
NUM_CLIENTS = 0
close_lock = threading.Lock()
CLOSE_SERVER = False


def handle_client(sock, screen, clock):
    """the main of the thread"""
    print('client logged')
    global NUM_CLIENTS
    num_lock.acquire()
    NUM_CLIENTS += 1
    num_lock.release()
    running_lock.acquire()
    finish = False
    pic_w = 0
    pic_h = 0
    try:
        while not finish:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = False
                    break
            data = recv_by_size(sock)
            com = data[:5].decode()
            data = data[5:]
            if com == 'SSIZE':
                print('changing size')
                pic_w = int(data.decode().split('#')[0])
                pic_h = int(data.decode().split('#')[1])
                print(pic_w,pic_h)
            if com == 'PIXEL':
                pixels = decompress(data)
                img = pygame.image.fromstring(pixels, (pic_w, pic_h), 'RGB')
                img = pygame.transform.scale(img, (WIDTH,HEIGHT))
                screen.blit(img, (0, 0))
            num_lock.acquire()
            if NUM_CLIENTS > 1:
                send_by_size(sock,'ENDST')
                NUM_CLIENTS -= 1
                finish = True
            num_lock.release()
            close_lock.acquire()
            if CLOSE_SERVER:
                send_by_size(sock, 'ENDST')
                finish = True
            close_lock.release()
            pygame.display.flip()
            clock.tick(60)
    finally:
        sock.close()
        running_lock.release()


def start_server():
    """starting the server thar shows screens of users"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    s = socket.socket()
    s.bind((IP,PORT))
    s.listen(3)
    s.settimeout(1)
    tid = 1
    threads = []
    close = False
    print ('accepting')
    while not close:
        try:
            sock, addr = s.accept()
            t = threading.Thread(target=handle_client,args=(sock, screen, clock))
            t.start()
            threads.append(t)
            tid += 1
        except socket.timeout:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            close_lock.acquire()
            if CLOSE_SERVER:
                close = True
            close_lock.release()

def stop_server():
    global CLOSE_SERVER
    close_lock.acquire()
    CLOSE_SERVER = True
    close_lock.release()


if __name__ == '__main__':
    start_server()

