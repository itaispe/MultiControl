from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import threading
from functools import partial
import time
import pyautogui
import actions_class
import pickle

class Recorder:
    def __init__(self,screen_x,screen_y):
        self.mouse_listener = MouseListener(on_click=partial(on_click, self), on_scroll=partial(on_scroll, self))
        self.keyboard_listener = KeyboardListener(on_press=partial(on_press, self),
                                                  on_release=partial(on_release, self))
        self.buffer = []
        self.lock = threading.Lock()
        self.screen_x = screen_x
        self.screen_y = screen_y

    def start_record(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def end_record(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def read_buffer(self):
        self.lock.acquire()
        lst = self.buffer
        self.buffer = []
        self.lock.release()
        return lst


# those four function are being called a-sync

def on_press(rec, key):
    """when key is pressed"""
    rec.lock.acquire()
    rec.buffer.append(actions_class.KeyPress(key,True))
    rec.lock.release()
    print("Key pressed: {0}".format(key))


def on_release(rec, key):
    """whe key is released"""
    rec.lock.acquire()
    rec.buffer.append(actions_class.KeyPress(key,False))
    rec.lock.release()
    print("Key released: {0}".format(key))


def on_click(rec, x, y, button, pressed):
    """when mouse is pressed/released"""
    is_right = False
    if button == 'right':
        is_right = True

    if pressed:
        rec.lock.acquire()
        rec.buffer.append(actions_class.MouseClick(x/rec.screen_x, y/rec.screen_y,is_right,False))
        rec.lock.release()
        # print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    else:
        rec.lock.acquire()
        rec.buffer.append(actions_class.MouseClick(x / rec.screen_x, y / rec.screen_y, is_right, True))
        rec.lock.release()
        # print('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))


def on_scroll(rec, x, y, dx, dy):
    """when mouse is scrolled"""
    rec.lock.acquire()
    rec.buffer.append(actions_class.MouseScroll(x/rec.screen_x,y/rec.screen_y,dx,dy))
    rec.lock.release()
   # print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))


def main():
    screen_x,screen_y = pyautogui.size()
    recorder = Recorder(screen_x,screen_y)
    recorder.start_record()
    time.sleep(10)
    recorder.end_record()
    buf = pickle.dumps(recorder.buffer)
    buffer = pickle.loads(buf)
    print('end')
    time.sleep(3)
    for i in buffer:
        i.commit()
        print('commited')


if __name__ == '__main__':
    main()
