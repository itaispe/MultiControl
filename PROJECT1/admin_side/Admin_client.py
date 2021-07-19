import socket
from key_mouse_logger import Recorder
import tkinter as tk
from tkinter import messagebox
import admin_gui
from functools import partial
from tcp_by_size import send_by_size,recv_by_size
import pyautogui
import pickle
import threading
from PIL import ImageGrab
import screen_share_admin
import time
from AES_class import AESCipher
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from os import urandom

IP = "192.168.99.112"
PORT = 12345
WINDOW_CLOSED = False
RECORD_ENDED = False
PRESSED_START = False
CLIENT_CONNECTED = 0
gui_lock = threading.Lock()


def generate_aes_key(sock):
    """creates a symmetrical AES key sends it to server using RSA"""
    data = recv_by_size(sock)
    pub_key = RSA.import_key(data,passphrase=None)
    rsa_cipher = PKCS1_OAEP.new(pub_key)
    aes_key = urandom(16)
    aes_key_ciphered = rsa_cipher.encrypt(aes_key)
    send_by_size(sock,aes_key_ciphered,True)
    return aes_key


def check_for_share(lst,streak):
    """checks if controller wants to switch screens"""
    for i in lst:
        if hasattr(i,'key'):
            print('key: '+str(i.key))
            if streak == 0:
                if str(i.key) == 'Key.ctrl_l' and i.is_press:
                    print('got first control')
                    streak += 1
                else:
                    streak = 0
            elif streak == 1:
                if (str(i.key) == 'Key.right' or str(i.key) == 'Key.left') and i.is_press:
                    streak += 1
                else:
                    streak = 0
            elif streak == 2:
                if (str(i.key) == 'Key.right' or str(i.key) == 'Key.left') and not i.is_press:
                    streak += 1
                else:
                    streak = 0
            elif streak == 3:
                if str(i.key) == 'Key.ctrl_l' and not i.is_press:
                    streak += 1
                    break
                else:
                    streak = 0
        else:
            streak = 0
    return streak


def end_pressed(end_var):
    gui_lock.acquire()
    end_var.set('True')
    gui_lock.release()


def start_pressed(start_press_var):
    gui_lock.acquire()
    start_press_var.set('True')
    gui_lock.release()


def call_last_pressed(sock):
    send_by_size(sock,'CALST')


def on_closing(root):
    global WINDOW_CLOSED
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        WINDOW_CLOSED = True


def take_screenshot(sock):
    im = ImageGrab.grab()
    img_to_send = im.tobytes()
    send_by_size(sock,'SCREN'.encode()+img_to_send,True)



def main(root):
    global CLIENT_CONNECTED
    global RECORD_ENDED
    global PRESSED_START
    s = socket.socket()
    s.connect((IP,PORT))
    send_by_size(s,'admin')
    logged_in = False
    tried = False
    is_old = False
    aes_key = generate_aes_key(s)
    aes_cipher = AESCipher(aes_key)
    while not logged_in:
        data = recv_by_size(s)
        command = data[:5].decode()
        if command == 'ISOLD':
            if tried:
                admin_gui.login_error(root,is_old)
            username, password, is_old = admin_gui.login_screen(root)
            print(username + ' ' + password + ' ' + str(is_old))
            admin_gui.clean_screen(root)
            if is_old:
                to_send = "OLD#" + username + "#" + password
            else:
                to_send = "NEW#" + username + "#" + password
            to_send = aes_cipher.encrypt(to_send)
            send_by_size(s,'LOGIN'.encode()+to_send,True)
            tried = True
        if command == 'LOGED':
            logged_in = True
            # send_by_size(s, 'DISCO')
        root.update()
        if WINDOW_CLOSED:
            break
    if logged_in:
        on_session = False
        ask_cli_num = True
        client_var, start_var = admin_gui.wait_for_start(window,s)
        window.update()
        s.settimeout(0.3)
        print('after setting timeout')
        while not on_session:
            if ask_cli_num:
                send_by_size(s,'CLNUM')
                ask_cli_num = False
            try:
                data = recv_by_size(s)
                com = data[:5].decode()
                if com == 'NUMCO':
                    gui_lock.acquire()
                    CLIENT_CONNECTED = int(data[5:].decode())
                    client_var.set('Number of connected clients: '+str(CLIENT_CONNECTED))
                    gui_lock.release()
                if com == 'READY':
                    on_session = True
            except socket.timeout:
                gui_lock.acquire()
                if start_var.get() == 'True':
                    ask_cli_num = False
                    send_by_size(s,'START')
                    print('sent start')
                gui_lock.release()
                window.update()

        x, y = pyautogui.size()
        rec = Recorder(x, y)
        rec.start_record()
        end_var = admin_gui.wait_for_end(window)
        t = threading.Thread(target=screen_share_admin.start_server)
        t.start()
        time.sleep(1)
        send_by_size(s,'SHRUP')
        streak = 0
        tmp_lst = []
        while on_session:
            try:
                data = recv_by_size(s).decode()
                if data[:5] == 'SCREN':
                    take_screenshot(s)
            except socket.timeout:
                window.update()
                gui_lock.acquire()
                if end_var.get() == 'True':
                    print('end pressed')
                    on_session = False
                    rec.end_record()
                gui_lock.release()
                lst = rec.read_buffer()
                streak = check_for_share(lst,streak)
                if streak == 0:
                    lst = tmp_lst + lst
                if 0 < streak < 4:
                    lst = lst[:-(streak-len(tmp_lst))]
                    tmp_lst += lst[-(streak-len(tmp_lst)):]
                if streak == 4:
                    print('GOTCHA')
                    send_by_size(s,'SHRUP')
                    lst = lst[:-(streak-len(tmp_lst))]
                    tmp_lst = []
                    streak = 0
                if lst:
                    send_by_size(s, 'INPUT'.encode() + pickle.dumps(lst), True)
                if not on_session:
                    screen_share_admin.stop_server()
                    send_by_size(s, 'ENDSE')
                    window.destroy()
                    break

    s.close()


if __name__ == '__main__':
    try:
        window = tk.Tk()
        window.state('zoomed')
        on_close = partial(on_closing,window)
        # window.protocol("WM_DELETE_WINDOW", on_close)
        main(window)
    except tk.TclError:
        exit()