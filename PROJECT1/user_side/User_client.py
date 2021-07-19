import socket
import pickle
from tcp_by_size import send_by_size, recv_by_size
import tkinter as tk
from tkinter import messagebox
from functools import partial
import screen_share_user
import threading
from AES_class import AESCipher
import json
from sys import argv
from os import system
from subprocess import Popen
import winreg as reg1
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from os import urandom

IP = "192.168.99.112"
PORT = 12345
WINDOW_CLOSED = False
FINISHED_CONNECTING = False
SCREEN_SHARE = False

name = ''
admins_name = ''
password = ''


def register_waiting_client(path):
    """registering the waiting client in the reg"""
    key1 = reg1.HKEY_CURRENT_USER
    key_value1 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    open1 = reg1.OpenKey(key1, key_value1, 0, reg1.KEY_ALL_ACCESS)
    reg1.SetValueEx(open1, "try_auto_run", 0, reg1.REG_SZ, path)


def generate_aes_key(sock):
    """creates a symmetrical AES key sends it to server using RSA"""
    data = recv_by_size(sock)
    pub_key = RSA.import_key(data,passphrase=None)
    rsa_cipher = PKCS1_OAEP.new(pub_key)
    aes_key = urandom(16)
    aes_key_ciphered = rsa_cipher.encrypt(aes_key)
    send_by_size(sock,aes_key_ciphered,True)
    return aes_key


def submit(admins_list, selected_admin):
    global FINISHED_CONNECTING
    print(selected_admin.get())
    if selected_admin.get() not in admins_list:
        messagebox.showerror(title='error', message='invalid admin name')
    else:
        FINISHED_CONNECTING = True


def on_closing(root):
    global WINDOW_CLOSED
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        WINDOW_CLOSED = True


def get_admin_name(root, admins_list):
    """show user log in page """
    global FINISHED_CONNECTING
    print(admins_list)
    root.configure(bg='#856ff8')
    head = tk.Label(text="Welcome to multi-Control !!!")
    head.config(font=("Courier", 44), bg='#856ff8')
    head.place(relx=0.5, rely=0.05, anchor='center')

    msg = tk.Label(text="choose the name of your controlling admin")
    msg.config(font=("Courier", 30), bg='#856ff8')
    msg.place(relx=0, rely=0.2, anchor='sw')

    admins_str = 'admins: ' + ', '.join(admins_list)
    log_label = tk.Label(text=admins_str)
    log_label.config(font=("Courier", 30), bg='#856ff8')
    log_label.place(relx=0.1, rely=0.3, anchor='sw')

    admins_name_var = tk.StringVar()
    pass_var = tk.StringVar()
    name_var = tk.StringVar()

    name_label = tk.Label(text='admin')
    name_label.config(font=("Courier", 30), bg='#856ff8')
    name_label.place(relx=0.4, rely=0.4, anchor='center')

    password_label = tk.Label(text='password')
    password_label.config(font=("Courier", 30), bg='#856ff8')
    password_label.place(relx=0.4, rely=0.5, anchor='center')

    confirm_label = tk.Label(text="user's name")
    confirm_label.config(font=("Courier", 30), bg='#856ff8')
    confirm_label.place(relx=0.46, rely=0.6, anchor='center')

    name_entry = tk.Entry(root, textvariable=admins_name_var, font=("Courier", 30))
    name_entry.place(relx=0.5, rely=0.37)

    passw_entry = tk.Entry(root, textvariable=pass_var, font=("Courier", 30), show='*')
    passw_entry.place(relx=0.5, rely=0.47)

    confirm_entry = tk.Entry(root, textvariable=name_var, font=("Courier", 30))
    confirm_entry.place(relx=0.6, rely=0.57)

    sign_up_act = partial(submit, admins_list, admins_name_var)
    sign_submit = tk.Button(root, text='Sign Up', command=sign_up_act)
    sign_submit.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    sign_submit.place(relx=0.5, rely=0.7)

    while not FINISHED_CONNECTING:
        try:
            root.update()
        except tk.TclError:
            break

    FINISHED_CONNECTING = False
    return name_var.get(), admins_name_var.get(), pass_var.get()


def main(root,use_last=False):
    global name, admins_name,password
    s = socket.socket()
    s.connect((IP, PORT))
    send_by_size(s, 'user')
    aes_key = generate_aes_key(s)
    aes_cipher = AESCipher(aes_key)
    connected = False
    tried = False
    while not connected:
        data = recv_by_size(s)
        com = data[:5].decode()
        data = data[5:]
        if com == 'ADLST':
            if use_last:
                with open('last_time_connected') as json_file:
                    lst = json.load(json_file)
                name = lst[0]
                admins_name = lst[1]
                password = lst[2]
            else:
                if tried:
                    messagebox.showerror('an error has a occurred','please try again in order to connect multi-control')
                name, admins_name, password = get_admin_name(root, pickle.loads(data))
            to_send = name + '#' + admins_name + '#' + password
            to_send = aes_cipher.encrypt(to_send)
            send_by_size(s, 'CONEC'.encode() + to_send, True)
            tried = True
        if com == 'LOGED':
            connected = True
    if connected:
        print('connected to admin')
        on_session = False
        root.destroy()
        while not on_session:
            data = recv_by_size(s)
            if data[:5].decode() == 'START':
                on_session = True
                send_by_size(s, 'BEGIN')
                print('started')
        while on_session:
            print('on session')
            data = recv_by_size(s)
            com = data[:5].decode()
            data = data[5:]
            if com == 'SHARE':
                lst = [data.decode()]
                t = threading.Thread(target=screen_share_user.share_screen,args=lst)
                t.start()
            if com == 'INPUT':
                buffer = pickle.loads(data)
                for i in buffer:
                    i.commit()
            if com == 'ENDSE':
                on_session = False
                lst = [name,admins_name,password]
                with open('last_time_connected','w+') as outfile:
                    json.dump(lst,outfile)

    register_waiting_client('E:\\yud_bet\\PROJECT1\\user_side\\waiting_client.py')
    Popen('python waiting_client.py')
    print('opened')


if __name__ == '__main__':
    try:
        window = tk.Tk()
        window.state('zoomed')
        on_close = partial(on_closing, window)
        # window.protocol("WM_DELETE_WINDOW", on_close)
        use_last = False
        if len(argv) > 1:
            IP = argv[1]
            if len(argv) == 3:
                if argv[2] == 'True':
                    use_last = True
        main(window,use_last)
    except tk.TclError:
        exit()
