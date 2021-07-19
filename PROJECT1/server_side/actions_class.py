import pyautogui
pyautogui.FAILSAFE = False
from pynput.mouse import Button,Controller as MouseController
from pynput.keyboard import Key,Controller as KeyboredController


class KeyPress:
    def __init__(self,key,is_press):
        self.key = key
        self.is_press = is_press

    def commit(self):
        keyboard = KeyboredController()
        if self.is_press:
            keyboard.press(self.key)
        else:
            keyboard.release(self.key)


class MouseClick:
    def __init__(self,x,y,is_right,is_release):
        """x and y are proportional to the screen size"""
        self.x = x
        self.y = y
        self.is_right = is_right
        self.is_release = is_release

    def commit(self):
        """multiplying x and y in screen size to get click location"""
        screen_x,screen_y = pyautogui.size()
        if self.is_right:
            if not self.is_release:
                pyautogui.mouseDown(button='right',x= (self.x*screen_x),y=(self.y*screen_y))
            else:
                pyautogui.mouseUp(button='right', x=(self.x * screen_x), y=(self.y * screen_y))
        else:
            if not self.is_release:
                pyautogui.mouseDown(button='left', x=(self.x * screen_x), y=(self.y * screen_y))
            else:
                pyautogui.mouseUp(button='left', x=(self.x * screen_x), y=(self.y * screen_y))


class MouseScroll:
    def __init__(self,x,y,dx,dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def commit(self):
        mouse = MouseController()
        screen_x,screen_y = pyautogui.size()
        pyautogui.moveTo(self.x * screen_x, self.y * screen_y)
        mouse.scroll(dx=self.dx,dy=self.dy)


def main():
    m1 = MouseClick(145/1920,43/1080,False,False)
    m2 = MouseClick(145/1920,43/1080,False,True)
    m1.commit()
    m2.commit()
    m1.commit()
    m2.commit()




if __name__ == '__main__':
    main()




