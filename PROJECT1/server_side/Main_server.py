import socket, threading, admins_sql
from tcp_by_size import recv_by_size, send_by_size
from admin_class import Admin
from user_class import User
import pickle, base64, hashlib
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from AES_class import AESCipher
from time import sleep


IP = '0.0.0.0'
PORT = 12345
ADMINS_DICT = {}
ADMINS_DICT_LOCK = threading.Lock()
RSA_KEY_SIZE = 1024 // 8

CLIENTS_TO_CONNECT = {} # key: user_ip value: admin ip (user : admin)
RELEASE_CLIENTS = []
WAITING_LOCK = threading.Lock()


def login(username, password,cli_s,cli_addr):
    """returns tuple: (bool,object)"""
    if admins_sql.check_password(username, password):
        ad = Admin(username,password,cli_s,cli_addr)
        return True, ad
    else:
        return False, None


def sign_up(username, password, cli_s,cli_addr):
    """getting new user information and verify it"""
    if admins_sql.check_new_username(username):
        ad = Admin(username, password, cli_s, cli_addr)
        admins_sql.insert_into_table(username, password)
        return True, ad
    return False, None


def add_admin_to_dict(admin):
    ADMINS_DICT_LOCK.acquire()
    ADMINS_DICT[admin.name] = admin
    ADMINS_DICT_LOCK.release()


def remove_admin_from_dict(admin):
    ADMINS_DICT_LOCK.acquire()
    del ADMINS_DICT[admin.name]
    ADMINS_DICT_LOCK.release()


def connect_user(cli_s, name, admin_name, password, cli_addr):
    """getting details pf new user, connecting him to admin if pass and name ar valid"""
    user = User(name, cli_addr, cli_s)
    ADMINS_DICT_LOCK.acquire()
    print('before checking')
    suc = user.add_admin(admin_name, password, list(ADMINS_DICT.values()))
    print('success of connection is: '+str(suc))
    ADMINS_DICT_LOCK.release()
    if suc:
        return True, user
    return False, None


def generate_aes_key(sock):
    """returns: an AES key created by the client which will be used for symmetrical encryption"""
    random_generator = Random.new().read
    key = RSA.generate(RSA_KEY_SIZE * 8, random_generator)
    send_by_size(sock, key.publickey().exportKey(format='PEM', passphrase=None, pkcs=1),True)
    cipher = PKCS1_OAEP.new(key)
    data = recv_by_size(sock)
    aes_key = cipher.decrypt(data)
    return aes_key


def handle_admin(cli_s, cli_addr, i):
    """main func that handles admin clients"""
    suc = False
    obj = None
    called_last = False
    aes_key = generate_aes_key(cli_s)
    aes_cipher = AESCipher(aes_key)
    while not suc:
        try:
            send_by_size(cli_s, 'ISOLD')
            data = recv_by_size(cli_s).decode()
            command = data[:5]
            data = data[5:]
            if command == 'LOGIN':
                data = aes_cipher.decrypt(data.encode())
                data_lst = data.split('#')
                h = hashlib.sha256()
                h.update(data_lst[2].encode())
                password = h.hexdigest()
                if data_lst[0] == 'OLD':
                    suc, obj = login(data_lst[1], password, cli_s,cli_addr)
                else:
                    suc, obj = sign_up(data_lst[1], password, cli_s,cli_addr)
            if command == 'DISCO':
                break
        except socket.error as e:
            print('client ', i, ' disconnected\n', e)
            cli_s.close()
            break
    finish = False
    while not finish:
        try:
            if suc:  # logged in, obj = client_admin_class object
                print('client logged')
                send_by_size(cli_s,'LOGED')
                on_session = False
                add_admin_to_dict(obj)
                cli_s.settimeout(None)
                while not on_session:
                    data = recv_by_size(cli_s)  # wait for start
                    command = data[:5].decode()
                    if command == 'START':
                        obj.start_session()
                        send_by_size(cli_s, 'READY')
                        on_session = True
                        remove_admin_from_dict(obj)
                    if command == 'CLNUM':
                        send_by_size(cli_s, 'NUMCO' + str(len(obj.connected_list)))
                    if command == 'CALST':
                        called_last = True
                        lst = obj.get_last_users()
                        WAITING_LOCK.acquire()
                        if lst:
                            for i in lst:
                                CLIENTS_TO_CONNECT[i] = obj.addr
                        WAITING_LOCK.release()
                    if command == 'DISCO':
                        obj.disconnect()
                        finish = True
                        cli_s.close()
                        break

                if on_session:
                    if not called_last:
                        lst = obj.get_last_users()
                        if lst:
                            WAITING_LOCK.acquire()
                            for i in lst:
                                RELEASE_CLIENTS.append(i)
                            WAITING_LOCK.release()

                while on_session:
                    try:
                        cli_s.settimeout(0.3)
                        data = recv_by_size(cli_s)
                        command = data[:5].decode()
                        data = data[5:]  # bytes
                        if command == 'SHRUP':
                            obj.share_up()
                        if command == 'SHRDW':
                            obj.share_down()
                        if command == 'INPUT':
                            obj.add_to_buffer(pickle.loads(data))
                        if command == 'ENDSE':
                            obj.end_session()
                            obj.save_to_ip_sql()
                        if command == 'SCREN':
                            obj.new_sql_row(data)
                    except socket.timeout:
                        obj.update_users_buffers()
                        obj.take_screenshot()
            else:
                finish = True
        except socket.error as e:
            print('client ', i, ' disconnected\n', e)
            obj.disconnect()
            cli_s.close()
            break


def handle_user(cli_s, cli_addr, i):
    """main func that handles user clients"""
    connected = False
    user = None
    aes_key = generate_aes_key(cli_s)
    aes_cipher = AESCipher(aes_key)
    while not connected:
        try:
            ADMINS_DICT_LOCK.acquire()
            send_by_size(cli_s, 'ADLST'.encode() + pickle.dumps(list(ADMINS_DICT.keys())),True)
            ADMINS_DICT_LOCK.release()
            data = recv_by_size(cli_s).decode()
            command = data[:5]
            data = data[5:]
            if command == "CONEC":
                data = aes_cipher.decrypt(data.encode())
                data_lst = data.split('#')
                h = hashlib.sha256()
                h.update(data_lst[2].encode())
                password = h.hexdigest()
                connected, user = connect_user(cli_s, data_lst[0], data_lst[1], password, cli_addr)
            if command == 'DISCO':
                break
        except socket.error as e:
            print('client ', i, ' disconnected\n', e)
            break
    finish = False
    while not finish:
        try:
            send_by_size(cli_s,'LOGED')
            print('user logged')
            if connected:
                on_session = False
                cli_s.settimeout(None)
                while not on_session:
                    data = recv_by_size(cli_s).decode()
                    command = data[:5]
                    if command == 'BEGIN':
                        on_session = True
                cli_s.settimeout(0.3)
                while on_session:
                    try:
                        data = recv_by_size(cli_s)
                        command = data[:5]
                        data = data[5:]
                        if command == 'STOPD':
                            on_session = False
                        if command == 'PROBL':
                            lst = user.admin.get_actions_by_number(int(data))
                            user.reset_buffer(lst)
                    except socket.timeout:
                        user.send_buffer()
            else:
                finish = True
        except socket.error as e:
            print('client ', i, ' disconnected\n', e)
            break


def handle_waiting_cli(cli_s, cli_addr, i):
    """main func that handles waiting clients"""
    finish = False
    while not finish:
        WAITING_LOCK.acquire()
        if cli_addr in CLIENTS_TO_CONNECT.keys():
            admin_ip = CLIENTS_TO_CONNECT.get(cli_addr)
            send_by_size(cli_s,'CONNE'+admin_ip)
            print('told cli to connect')
            CLIENTS_TO_CONNECT.pop(cli_addr)
            finish = True
        if cli_addr in RELEASE_CLIENTS:
            print('told cli to dis')
            send_by_size(cli_s,'STOPP')
            finish = True
            RELEASE_CLIENTS.remove(cli_addr)
        WAITING_LOCK.release()
        sleep(1)
    cli_s.close()
    print('waiting client finished')


def handle_client(cli_s, cli_addr, i):
    """dividing the clients according to their type"""
    print('new client')
    data = recv_by_size(cli_s).decode()
    if data == 'admin':
        print('new admin')
        handle_admin(cli_s, cli_addr, i)
    if data == 'user':
        print('new user')
        handle_user(cli_s, cli_addr, i)
    if data == 'waiting':
        print('new waiting client')
        handle_waiting_cli(cli_s, cli_addr, i)


def main():
    s = socket.socket()
    s.bind((IP, PORT))
    s.listen(10)
    i = 1
    threads = []
    while True:
        cli_s, cli_addr = s.accept()
        t = threading.Thread(target=handle_client,args=(cli_s, cli_addr[0], i))
        t.start()
        threads.append(t)
        i += 1


if __name__ == '__main__':
    main()
