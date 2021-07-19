import threading
import tcp_by_size
import time
import photos_sql

import pickle
import base64
import users_ip_sql

screenshot_time = 60
screenshot_action = 10000000000000


class Admin:
    def __init__(self, name, password, sock, addr):
        self.name = name
        self.password = password
        self.sock = sock
        self.connected_list = []
        self.buffer = []
        self.admin_lock = threading.Lock()
        self.status = False
        self.session_start = None
        self.action_counter = 0
        self.all_actions = []
        self.sharing_user_num = 0
        self.addr = addr

    def add_to_buffer(self, action):
        """adds list of actions to the admins buffer"""
        self.admin_lock.acquire()
        self.buffer += action
        self.all_actions += action
        self.action_counter += len(action)
        self.admin_lock.release()

    def add_user(self, user):
        """adding user to the connected list"""
        self.admin_lock.acquire()
        self.connected_list.append(user)
        tcp_by_size.send_by_size(self.sock,'NUMCO'+str(len(self.connected_list)))
        self.admin_lock.release()

    def start_session(self):
        self.status = True
        self.session_start = time.time()
        for i in self.connected_list:
            tcp_by_size.send_by_size(i.sock, 'START')

    def update_users_buffers(self):
        """emptying the admins buffer into the users buffer"""
        self.admin_lock.acquire()
        if self.buffer:
            for i in self.connected_list:
                i.user_lock.acquire()
                i.buffer += self.buffer
                i.user_lock.release()
        self.buffer = []
        self.admin_lock.release()

    def take_screenshot(self):
        if time.time() - self.session_start > screenshot_time and self.action_counter > screenshot_action:
            tcp_by_size.send_by_size(self.sock, 'SCREN')

    def end_session(self):
        self.status = False
        for i in self.connected_list:
            tcp_by_size.send_by_size(i.sock,'ENDSE')

    def disconnect(self):
        if self.status:
            self.end_session()
        for i in self.connected_list:
            tcp_by_size.send_by_size(i.sock,'FINIS')

    def get_actions_by_number(self,action_num):
        """called in case a user is missing actions, receives the last number of action that was valid
        returns all action have been done since that number"""
        self.admin_lock.acquire()
        lst = self.all_actions[action_num-1:]
        self.admin_lock.release()
        return lst

    def new_sql_row(self,photo):
        photos_sql.insert_new_photo(time.time()-self.session_start,self.name,len(self.connected_list),photo)

    def share_up(self):
        """telling a user to send screen pictures to his admin"""
        tcp_by_size.send_by_size(self.connected_list[self.sharing_user_num].sock,'SHARE'+self.addr)
        self.sharing_user_num += 1
        if self.sharing_user_num == len(self.connected_list):
            self.sharing_user_num = 0

    def share_down(self):
        self.sharing_user_num -=1
        if self.sharing_user_num < 0:
            self.sharing_user_num = len(self.connected_list) - 1
        tcp_by_size.send_by_size(self.connected_list[self.sharing_user_num].sock, 'SHARE'+self.addr)

    def save_to_ip_sql(self):
        """saves connected list IP addresses in the SQL"""
        users_ip = []
        for i in self.connected_list:
            users_ip.append(i.address)
        users_ip_sql.insert_into_table(base64.b64encode(pickle.dumps(users_ip)).decode(),self.addr)

    def get_last_users(self):
        """:returns the IP addresses of the last connected users"""
        lst = users_ip_sql.get_user_ip_list(self.addr)
        if lst:
            return pickle.loads(base64.b64decode(lst.encode()))
        else:
            return None

    def get_connected_ip(self):
        """returns a list of the IP of the curren connected clients"""
        lst = []
        for i in self.connected_list:
            lst.append(i.address)
        return lst
