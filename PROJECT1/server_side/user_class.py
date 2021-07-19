import pickle
import threading
import tcp_by_size


class User:
    def __init__(self, name, address, sock):
        self.name = name
        self.address = address
        self.sock = sock
        self.buffer = []
        self.admin = None
        self.user_lock = threading.Lock()

    def send_buffer(self):
        """sending the actions in the buffer to the user"""
        self.user_lock.acquire()
        if self.buffer:
            lst = pickle.dumps(self.buffer)
            tcp_by_size.send_by_size(self.sock,'INPUT'.encode()+lst, True)
            self.buffer = []
        self.user_lock.release()

    def add_admin(self, name,password,lst):
        """connecting the user to the admin he requested"""
        suc = False
        for i in lst:
            print('admin name: '+i.name)
            print('name: '+name)
            if i.name == name:
                if i.password == password:
                    print('passwords equal')
                    suc = True
                    self.admin = i
                    i.add_user(self)
        return suc

    def reset_buffer(self,action):
        self.user_lock.acquire()
        self.buffer = action
        self.user_lock.release()
